"""
Example integration script showing how to use the retry prediction model.

This demonstrates basic usage patterns for integrating the retry prediction
model into existing load balancer infrastructure.

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

def basic_prediction_example():
    """Demonstrate basic retry prediction functionality."""
    print("Basic Prediction Example")
    print("=" * 40)
    
    try:
        from prediction_api import RetryPredictor
        
        # Initialize the predictor
        print("Loading model...")
        predictor = RetryPredictor()
        
        # Example request scenarios
        scenarios = [
            {
                'name': 'High-latency 5xx error',
                'data': {
                    'response_time_ms': 1500,
                    'status_code': 500,
                    'bytes_sent': 1024,
                    'anomaly_score': 3.2
                }
            },
            {
                'name': 'Fast successful request',
                'data': {
                    'response_time_ms': 150,
                    'status_code': 200,
                    'bytes_sent': 2048,
                    'anomaly_score': 0.1
                }
            },
            {
                'name': 'Timeout scenario',
                'data': {
                    'response_time_ms': 5000,
                    'status_code': 504,
                    'bytes_sent': 0,
                    'anomaly_score': 4.8
                }
            }
        ]
        
        # Make predictions for each scenario
        for scenario in scenarios:
            try:
                probability = predictor.predict_retry_probability(scenario['data'])
                print(f"\n📊 {scenario['name']}")
                print(f"   Retry probability: {probability:.1%}")
                
                # Provide interpretation
                if probability > 0.7:
                    print("   🔴 High retry risk - Consider circuit breaker")
                elif probability > 0.4:
                    print("   🟡 Medium retry risk - Monitor closely")
                else:
                    print("   🟢 Low retry risk - Normal processing")
                    
            except Exception as e:
                print(f"   ❌ Prediction failed: {e}")
        
    except ImportError as e:
        print(f"❌ Cannot import prediction module: {e}")
        print("Make sure you've installed dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Prediction example failed: {e}")

def load_balancer_integration_example():
    """Show how to integrate with a hypothetical load balancer."""
    print("\n🔄 Load Balancer Integration Example")
    print("=" * 45)
    
    # Simulated load balancer logic
    class SimpleLoadBalancer:
        def __init__(self):
            self.servers = ['server-1', 'server-2', 'server-3']
            self.retry_predictor = None
            
            # Try to initialize predictor
            try:
                sys.path.append('src')
                from prediction_api import RetryPredictor
                self.retry_predictor = RetryPredictor()
                print("✅ Retry predictor integrated")
            except Exception as e:
                print(f"⚠️  Retry predictor not available: {e}")
        
        def route_request(self, request_data):
            """Route request with retry prediction."""
            print(f"\n🔄 Routing request...")
            
            if self.retry_predictor:
                try:
                    retry_prob = self.retry_predictor.predict_retry_probability(request_data)
                    print(f"   Retry probability: {retry_prob:.1%}")
                    
                    # Route based on prediction
                    if retry_prob > 0.6:
                        # High retry risk - use circuit breaker or alternate routing
                        print("   🛡️  High retry risk detected")
                        print("   → Routing to backup server or showing cached response")
                        return "backup-server"
                    else:
                        # Normal routing
                        print("   ✅ Normal retry risk")
                        print("   → Routing to primary server")
                        return self.servers[0]
                        
                except Exception as e:
                    print(f"   ⚠️  Prediction failed, using default routing: {e}")
            
            # Fallback to round-robin
            return self.servers[0]
    
    # Example usage
    lb = SimpleLoadBalancer()
    
    # Test different request types
    test_requests = [
        {
            'response_time_ms': 750,
            'status_code': 500,
            'bytes_sent': 1024,
            'anomaly_score': 2.5
        },
        {
            'response_time_ms': 120,
            'status_code': 200,
            'bytes_sent': 4096,
            'anomaly_score': 0.2
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📨 Request {i}:")
        server = lb.route_request(request)
        print(f"   → Routed to: {server}")

def monitoring_example():
    """Show how to monitor retry predictions."""
    print("\n📊 Monitoring Example")
    print("=" * 25)
    
    # Simulated monitoring metrics
    print("Sample monitoring metrics that could be tracked:")
    print("  • Retry predictions per second: 1,250")
    print("  • Average prediction latency: 8ms")
    print("  • Prediction accuracy: 94.2%")
    print("  • Circuit breaker activations: 12 (last hour)")
    print("  • Cost savings: $1,340 (estimated monthly)")

def main():
    """Run all examples."""
    print("🚀 Load Balancer Retry Prediction - Integration Examples")
    print("=" * 65)
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run examples
    basic_prediction_example()
    load_balancer_integration_example()
    monitoring_example()
    
    print("\n" + "=" * 65)
    print("📚 For more detailed examples, see:")
    print("  • docs/api_documentation.md")
    print("  • docs/deployment_guide.md")
    print("  • notebooks/retry_prediction_analysis.ipynb")
    
    print(f"\n📧 Questions? Contact: Fares Chehidi (fareschehidi@gmail.com)")

if __name__ == "__main__":
    main()
