"""
Data processing utilities for retry prediction.

Author: Fares Chehidi (fareschehidi@gmail.com)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


def load_telemetry_data(file_path):
    """
    Load and preprocess telemetry data.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Preprocessed telemetry data
    """
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def create_retry_features(df):
    """
    Create features for retry prediction model.
    
    Args:
        df (pd.DataFrame): Raw telemetry data
        
    Returns:
        tuple: (features_df, target_series, label_encoders)
    """
    df_model = df.copy()
    
    # Create target variable
    df_model['has_retry'] = (df_model['retry_count'] > 0).astype(int)
    
    # Temporal features
    df_model['hour'] = df_model['timestamp'].dt.hour
    df_model['day_of_week'] = df_model['timestamp'].dt.dayofweek
    df_model['is_weekend'] = (df_model['day_of_week'] >= 5).astype(int)
    df_model['is_peak_hour'] = ((df_model['hour'] >= 9) & (df_model['hour'] <= 17)).astype(int)
    
    # Response time features
    df_model['response_time_log'] = np.log1p(df_model['response_time_ms'])
    df_model['is_slow_response'] = (df_model['response_time_ms'] > 500).astype(int)
    
    # Error indicators
    df_model['is_client_error'] = (df_model['status_code'].between(400, 499)).astype(int)
    df_model['is_server_error'] = (df_model['status_code'] >= 500).astype(int)
    df_model['is_success'] = (df_model['status_code'].between(200, 299)).astype(int)
    
    # Categorical encoding
    label_encoders = {}
    categorical_columns = ['server_id', 'region', 'request_method', 'failure_type', 'method_category', 'latency_bucket']
    
    for col in categorical_columns:
        le = LabelEncoder()
        df_model[f'{col}_encoded'] = le.fit_transform(df_model[col].astype(str))
        label_encoders[col] = le
    
    # Additional features
    df_model['high_anomaly'] = (df_model['anomaly_score'] > df_model['anomaly_score'].quantile(0.75)).astype(int)
    df_model['bytes_per_ms'] = df_model['bytes_sent'] / (df_model['response_time_ms'] + 1)
    
    # Define feature columns
    feature_columns = [
        'response_time_ms', 'response_time_log', 'bytes_sent', 'bytes_per_ms',
        'anomaly_score', 'hour', 'day_of_week', 'is_weekend', 'is_peak_hour',
        'is_slow_response', 'is_client_error', 'is_server_error', 'is_success',
        'high_anomaly'
    ] + [f'{col}_encoded' for col in categorical_columns]
    
    return df_model[feature_columns], df_model['has_retry'], label_encoders


def validate_request_data(data):
    """
    Validate incoming request data for prediction.
    
    Args:
        data (dict): Request data
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['response_time_ms', 'status_code', 'bytes_sent', 'anomaly_score']
    
    for field in required_fields:
        if field not in data:
            return False
        
        if not isinstance(data[field], (int, float)):
            return False
    
    return True


def calculate_business_metrics(df):
    """
    Calculate business impact metrics from telemetry data.
    
    Args:
        df (pd.DataFrame): Telemetry data
        
    Returns:
        dict: Business metrics
    """
    total_requests = len(df)
    retry_requests = df['retry_count'].gt(0).sum()
    retry_rate = retry_requests / total_requests
    
    # Error rates by type
    error_rate_4xx = df['status_code'].between(400, 499).mean()
    error_rate_5xx = df['status_code'].ge(500).mean()
    
    # Response time statistics
    avg_response_time = df['response_time_ms'].mean()
    p95_response_time = df['response_time_ms'].quantile(0.95)
    
    # Regional analysis
    regional_stats = df.groupby('region').agg({
        'retry_count': 'mean',
        'response_time_ms': 'mean',
        'status_code': lambda x: (x >= 400).mean()
    }).round(3)
    
    return {
        'total_requests': total_requests,
        'retry_rate': retry_rate,
        'error_rate_4xx': error_rate_4xx,
        'error_rate_5xx': error_rate_5xx,
        'avg_response_time': avg_response_time,
        'p95_response_time': p95_response_time,
        'regional_stats': regional_stats.to_dict()
    }
