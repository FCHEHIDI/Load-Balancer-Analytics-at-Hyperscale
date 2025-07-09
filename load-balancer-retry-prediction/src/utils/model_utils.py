"""
Model management utilities.

Author: Fares Chehidi (fareschehidi@gmail.com)
"""

import joblib
import numpy as np
from datetime import datetime


def load_model(model_path):
    """
    Load trained model artifacts.
    
    Args:
        model_path (str): Path to the model file
        
    Returns:
        dict: Model artifacts
    """
    return joblib.load(model_path)


def save_model(model_artifacts, model_path):
    """
    Save model artifacts to file.
    
    Args:
        model_artifacts (dict): Model and preprocessing components
        model_path (str): Output file path
    """
    joblib.dump(model_artifacts, model_path)


def predict_retry_probability(model_artifacts, request_data):
    """
    Make retry prediction using loaded model.
    
    Args:
        model_artifacts (dict): Loaded model components
        request_data (dict): Request features
        
    Returns:
        float: Retry probability (0-1)
    """
    import pandas as pd
    
    model = model_artifacts['model']
    scaler = model_artifacts['scaler']
    label_encoders = model_artifacts['label_encoders']
    feature_columns = model_artifacts['feature_columns']
    
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
                    df_pred[f'{col}_encoded'] = 0
    
    # Extract features and predict
    X_pred = df_pred[feature_columns]
    
    if model_artifacts['model_name'] == 'Logistic Regression':
        X_pred_scaled = scaler.transform(X_pred)
        prob = model.predict_proba(X_pred_scaled)[0, 1]
    else:
        prob = model.predict_proba(X_pred)[0, 1]
    
    return min(max(prob, 0.0), 1.0)


def get_recommended_action(retry_probability):
    """
    Get recommended action based on retry probability.
    
    Args:
        retry_probability (float): Probability of retry
        
    Returns:
        str: Recommended action
    """
    if retry_probability > 0.8:
        return "CIRCUIT_BREAK"
    elif retry_probability > 0.6:
        return "ROUTE_BACKUP"
    elif retry_probability > 0.4:
        return "INCREASE_TIMEOUT"
    else:
        return "ALLOW"


def validate_model_health(model_artifacts):
    """
    Validate that model artifacts are properly loaded.
    
    Args:
        model_artifacts (dict): Model components
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_keys = ['model', 'scaler', 'label_encoders', 'feature_columns', 'model_name', 'auc_score']
    
    for key in required_keys:
        if key not in model_artifacts:
            return False
    
    return True


def create_prediction_response(retry_probability, model_version="1.0"):
    """
    Create standardized prediction response.
    
    Args:
        retry_probability (float): Predicted retry probability
        model_version (str): Version of the model
        
    Returns:
        dict: Formatted response
    """
    action = get_recommended_action(retry_probability)
    confidence = 'HIGH' if abs(retry_probability - 0.5) > 0.3 else 'MEDIUM'
    
    return {
        'retry_probability': round(retry_probability, 4),
        'confidence_level': confidence,
        'recommended_action': action,
        'prediction_timestamp': datetime.now().isoformat(),
        'model_version': model_version
    }
