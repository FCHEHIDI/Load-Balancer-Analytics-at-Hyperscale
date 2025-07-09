# API Documentation

## Retry Prediction API

The Retry Prediction API provides real-time predictions for client retry behavior in load balancer environments.

### Base URL

```
http://localhost:5000
```

### Authentication

No authentication required for the current version.

### Endpoints

#### POST /predict_retry

Predict the probability of a client retry for a given request.

**Request Body:**

```json
{
  "response_time_ms": 750,
  "status_code": 500,
  "bytes_sent": 1024,
  "anomaly_score": 2.5,
  "server_id": "server-001",
  "region": "us-east-1",
  "request_method": "GET",
  "failure_type": "Internal Error",
  "method_category": "Read",
  "latency_bucket": "Slow"
}
```

**Required Fields:**
- `response_time_ms` (integer): Response time in milliseconds
- `status_code` (integer): HTTP status code
- `bytes_sent` (integer): Response payload size in bytes
- `anomaly_score` (float): Anomaly detection score

**Optional Fields:**
- `server_id` (string): Server identifier
- `region` (string): Geographic region
- `request_method` (string): HTTP method (GET, POST, etc.)
- `failure_type` (string): Type of failure if applicable
- `method_category` (string): Category of operation
- `latency_bucket` (string): Latency classification

**Response:**

```json
{
  "retry_probability": 0.8456,
  "confidence_level": "HIGH",
  "recommended_action": "CIRCUIT_BREAK",
  "prediction_timestamp": "2025-07-09T10:30:00",
  "model_version": "1.0"
}
```

**Response Fields:**
- `retry_probability`: Probability of retry (0.0 to 1.0)
- `confidence_level`: HIGH or MEDIUM based on prediction certainty
- `recommended_action`: Suggested action (ALLOW, INCREASE_TIMEOUT, ROUTE_BACKUP, CIRCUIT_BREAK)
- `prediction_timestamp`: When the prediction was made
- `model_version`: Version of the model used

#### GET /health

Health check endpoint for monitoring and load balancer probes.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### GET /model_info

Get information about the currently loaded model.

**Response:**

```json
{
  "model_name": "Logistic Regression",
  "auc_score": 1.0,
  "feature_count": 20
}
```

### Error Responses

#### 400 Bad Request

Missing required fields or invalid input.

```json
{
  "error": "Missing required field: response_time_ms"
}
```

#### 500 Internal Server Error

Server error during prediction.

```json
{
  "error": "Model prediction failed"
}
```

### Usage Examples

#### Python

```python
import requests
import json

# Prepare request data
data = {
    "response_time_ms": 750,
    "status_code": 500,
    "bytes_sent": 1024,
    "anomaly_score": 2.5
}

# Make prediction request
response = requests.post(
    "http://localhost:5000/predict_retry",
    json=data
)

result = response.json()
print(f"Retry probability: {result['retry_probability']:.2%}")
print(f"Recommended action: {result['recommended_action']}")
```

#### cURL

```bash
curl -X POST http://localhost:5000/predict_retry \
  -H "Content-Type: application/json" \
  -d '{
    "response_time_ms": 750,
    "status_code": 500,
    "bytes_sent": 1024,
    "anomaly_score": 2.5
  }'
```

### Performance Considerations

- **Latency**: Typical response time < 10ms
- **Throughput**: Supports thousands of requests per second
- **Caching**: Consider implementing Redis for frequently requested predictions
- **Scaling**: Deploy multiple instances behind a load balancer for high availability

### Monitoring

The API provides built-in logging and should be monitored for:
- Response latency
- Error rates
- Prediction accuracy
- Resource utilization

### Contact

For API support or questions:

**Fares Chehidi**  
Email: fareschehidi28@gmail.com
