"""
Production-ready API service for retry prediction.

This module provides a Flask-based REST API for predicting client retry
behavior in load balancer environments.

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class RetryPredictor:
    """Production-ready retry prediction service."""
    
    def __init__(self, model_path='../models/retry_model.pkl'):
        """
        Initialize the predictor with trained model artifacts.
        
        Args:
            model_path (str): Path to the saved model file
        """
        self.model_path = model_path
        self.model_artifacts = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessing components."""
        try:
            self.model_artifacts = joblib.load(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict_retry_probability(self, request_data):
        """
        Predict the probability of a client retry for given request data.
        
        Args:
            request_data (dict): Dictionary containing request features
            
        Returns:
            float: Probability of retry (0-1)
        """
        try:
            model = self.model_artifacts['model']
            scaler = self.model_artifacts['scaler']
            label_encoders = self.model_artifacts['label_encoders']
            feature_columns = self.model_artifacts['feature_columns']
            
            # Create DataFrame from input
            df_pred = pd.DataFrame([request_data])
            
            # Apply feature engineering
            df_pred['response_time_log'] = np.log1p(df_pred['response_time_ms'])
            df_pred['is_slow_response'] = (df_pred['response_time_ms'] > 500).astype(int)
            df_pred['is_client_error'] = (df_pred['status_code'].between(400, 499)).astype(int)
            df_pred['is_server_error'] = (df_pred['status_code'] >= 500).astype(int)
            df_pred['is_success'] = (df_pred['status_code'].between(200, 299)).astype(int)
            df_pred['bytes_per_ms'] = df_pred['bytes_sent'] / (df_pred['response_time_ms'] + 1)
            df_pred['high_anomaly'] = (df_pred['anomaly_score'] > 2.0).astype(int)
            
            # Encode categorical variables
            categorical_columns = ['server_id', 'region', 'request_method', 'failure_type', 'method_category', 'latency_bucket']
            for col in categorical_columns:
                if col in df_pred.columns:
                    le = label_encoders.get(col)
                    if le:
                        try:
                            df_pred[f'{col}_encoded'] = le.transform(df_pred[col].astype(str))
                        except ValueError:
                            df_pred[f'{col}_encoded'] = 0  # Default for unseen categories
            
            # Extract features and predict
            X_pred = df_pred[feature_columns]
            
            # Scale features for logistic regression
            if self.model_artifacts['model_name'] == 'Logistic Regression':
                X_pred_scaled = scaler.transform(X_pred)
                prob = model.predict_proba(X_pred_scaled)[0, 1]
            else:
                prob = model.predict_proba(X_pred)[0, 1]
            
            return min(max(prob, 0.0), 1.0)  # Ensure probability bounds
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.5  # Conservative fallback

# Initialize predictor
predictor = RetryPredictor()

@app.route('/predict_retry', methods=['POST'])
def predict_retry():
    """API endpoint for retry prediction."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['response_time_ms', 'status_code', 'bytes_sent', 'anomaly_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add current timestamp features if not provided
        now = datetime.now()
        data.setdefault('hour', now.hour)
        data.setdefault('day_of_week', now.weekday())
        data.setdefault('is_weekend', int(now.weekday() >= 5))
        data.setdefault('is_peak_hour', int(9 <= now.hour <= 17))
        
        # Make prediction
        retry_prob = predictor.predict_retry_probability(data)
        
        # Determine action based on probability
        action = "ALLOW"
        if retry_prob > 0.8:
            action = "CIRCUIT_BREAK"
        elif retry_prob > 0.6:
            action = "ROUTE_BACKUP"
        elif retry_prob > 0.4:
            action = "INCREASE_TIMEOUT"
        
        return jsonify({
            'retry_probability': round(retry_prob, 4),
            'confidence_level': 'HIGH' if abs(retry_prob - 0.5) > 0.3 else 'MEDIUM',
            'recommended_action': action,
            'prediction_timestamp': datetime.now().isoformat(),
            'model_version': '1.0'
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer."""
    return jsonify({'status': 'healthy', 'model_loaded': True})

@app.route('/model_info', methods=['GET'])
def model_info():
    """Return information about the loaded model."""
    if predictor.model_artifacts:
        return jsonify({
            'model_name': predictor.model_artifacts['model_name'],
            'auc_score': predictor.model_artifacts['auc_score'],
            'feature_count': len(predictor.model_artifacts['feature_columns'])
        })
    else:
        return jsonify({'error': 'Model not loaded'}), 500

if __name__ == '__main__':
    print("Retry Prediction API starting...")
    print("• Model loaded successfully")
    print("• Endpoints: /predict_retry, /health, /model_info")
    app.run(host='0.0.0.0', port=5000, debug=False)
