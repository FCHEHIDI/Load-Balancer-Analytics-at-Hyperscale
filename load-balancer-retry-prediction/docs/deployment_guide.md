# Deployment Guide

## Production Deployment Guide for Load Balancer Retry Prediction

This guide provides step-by-step instructions for deploying the retry prediction model in production environments.

### Prerequisites

#### System Requirements

**Minimum Requirements:**
- CPU: 2+ cores
- RAM: 4GB
- Storage: 1GB
- Network: Stable connection to load balancer

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB
- Storage: 10GB
- Network: High availability setup with redundancy

#### Software Requirements

- Python 3.8 or higher
- Docker (optional but recommended)
- Kubernetes (for container orchestration)
- Redis (for caching, optional)

### Installation

#### Option 1: Direct Python Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd load-balancer-retry-prediction
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify model file:**
   ```bash
   ls models/retry_model.pkl
   ```

5. **Start the API service:**
   ```bash
   cd src
   python prediction_api.py
   ```

#### Option 2: Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 5000
   
   CMD ["python", "src/prediction_api.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t retry-predictor .
   docker run -p 5000:5000 retry-predictor
   ```

### Configuration

#### Environment Variables

Set these environment variables for production:

```bash
export MODEL_PATH="/path/to/retry_model.pkl"
export API_PORT="5000"
export LOG_LEVEL="INFO"
export REDIS_URL="redis://localhost:6379"  # Optional
```

#### Nginx Configuration

For production, use Nginx as a reverse proxy:

```nginx
upstream retry_predictor {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;  # Multiple instances for HA
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /predict_retry {
        proxy_pass http://retry_predictor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 1s;
        proxy_timeout 5s;
    }
    
    location /health {
        proxy_pass http://retry_predictor;
        access_log off;
    }
}
```

### Kubernetes Deployment

#### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retry-predictor
  labels:
    app: retry-predictor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retry-predictor
  template:
    metadata:
      labels:
        app: retry-predictor
    spec:
      containers:
      - name: retry-predictor
        image: retry-predictor:latest
        ports:
        - containerPort: 5000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: retry-predictor-service
spec:
  selector:
    app: retry-predictor
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl get pods -l app=retry-predictor
kubectl get service retry-predictor-service
```

### Monitoring and Alerting

#### Prometheus Metrics

Add monitoring endpoints to the API:

```python
from prometheus_client import Counter, Histogram, generate_latest

prediction_counter = Counter('retry_predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

#### Grafana Dashboard

Create dashboards to monitor:
- Request rate and latency
- Error rates
- Model prediction distribution
- System resource usage

#### Alerting Rules

Set up alerts for:
- High error rates (>5%)
- High latency (>100ms P95)
- Service unavailability
- Unusual prediction patterns

### Load Balancer Integration

#### HAProxy Configuration

```haproxy
backend retry_prediction_api
    balance roundrobin
    option httpchk GET /health
    server api1 127.0.0.1:5000 check
    server api2 127.0.0.1:5001 check

frontend load_balancer
    bind *:80
    # Capture request metrics
    capture request header X-Request-ID len 32
    
    # Route prediction requests
    acl is_prediction_request path_beg /predict_retry
    use_backend retry_prediction_api if is_prediction_request
    
    # Apply prediction logic (requires HAProxy Lua script)
    http-request lua.predict_retry if is_prediction_request
```

#### Integration Code Example

```python
# Example integration with load balancer
import requests

def get_retry_prediction(request_metrics):
    """Get retry prediction for request routing decisions."""
    try:
        response = requests.post(
            'http://retry-predictor/predict_retry',
            json=request_metrics,
            timeout=0.01  # 10ms timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['retry_probability'], result['recommended_action']
        else:
            return 0.5, 'ALLOW'  # Fallback
            
    except requests.RequestException:
        return 0.5, 'ALLOW'  # Fallback on error

def route_request(request_data):
    """Route request based on retry prediction."""
    retry_prob, action = get_retry_prediction(request_data)
    
    if action == 'CIRCUIT_BREAK':
        return 'circuit_breaker'
    elif action == 'ROUTE_BACKUP':
        return 'backup_servers'
    else:
        return 'primary_servers'
```

### Testing

#### Unit Tests

```bash
cd tests
python -m pytest test_prediction_api.py -v
```

#### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 -p test_data.json -T application/json http://localhost:5000/predict_retry

# Using wrk
wrk -t10 -c100 -d30s -s post.lua http://localhost:5000/predict_retry
```

### Security Considerations

1. **Network Security:**
   - Use HTTPS in production
   - Implement rate limiting
   - Set up firewall rules

2. **Authentication:**
   - Consider API keys for access control
   - Implement request signing if needed

3. **Data Protection:**
   - Log minimal sensitive information
   - Implement data retention policies

### Troubleshooting

#### Common Issues

1. **Model Loading Errors:**
   ```bash
   # Check model file permissions
   ls -la models/retry_model.pkl
   
   # Verify Python path
   python -c "import joblib; print(joblib.load('models/retry_model.pkl'))"
   ```

2. **High Latency:**
   - Check system resources
   - Verify model complexity
   - Consider caching frequent predictions

3. **Memory Issues:**
   - Monitor memory usage
   - Adjust container limits
   - Consider model optimization

#### Logs

Monitor application logs for:
```bash
tail -f /var/log/retry-predictor/app.log
```

### Rollback Procedures

1. **Immediate Rollback:**
   ```bash
   kubectl rollout undo deployment/retry-predictor
   ```

2. **Fallback Mode:**
   - Configure load balancer to use simple heuristics
   - Route all traffic to primary servers
   - Disable retry prediction temporarily

### Maintenance

#### Model Updates

1. **Prepare new model:**
   ```bash
   cp new_retry_model.pkl models/retry_model_v2.pkl
   ```

2. **Blue-Green Deployment:**
   ```bash
   kubectl set image deployment/retry-predictor retry-predictor=retry-predictor:v2
   kubectl rollout status deployment/retry-predictor
   ```

3. **Validation:**
   - Monitor prediction accuracy
   - Compare with previous model performance
   - Rollback if issues detected

### Support

For deployment support or issues:

**Fares Chehidi**  
Email: fareschehidi28@gmail.com

Include the following in support requests:
- Deployment environment details
- Error logs and stack traces
- System resource utilization
- Network configuration details
