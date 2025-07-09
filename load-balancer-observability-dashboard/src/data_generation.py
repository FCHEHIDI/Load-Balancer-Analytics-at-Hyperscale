"""
Synthetic Data Generator for Load Balancer Analytics

This module provides comprehensive synthetic data generation for load balancer telemetry,
simulating realistic traffic patterns, server metrics, and operational scenarios for
testing and demonstration of observability dashboards.

Key Features:
- Request log generation with realistic traffic patterns
- Server metrics simulation with resource utilization tracking
- Anomaly injection for testing alerting systems
- Regional and temporal traffic distribution modeling
- Configurable data volume and time ranges

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

import random
import datetime
import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadBalancerDataGenerator:
    """
    Synthetic data generator for load balancer telemetry and server metrics.
    
    This class simulates realistic traffic patterns and infrastructure metrics
    for testing observability dashboards and analytics pipelines. It generates
    both request-level logs and server performance metrics with configurable
    anomalies and traffic patterns.
    
    Attributes:
        servers (List[str]): List of server identifiers
        regions (List[str]): Available deployment regions
        request_methods (List[str]): HTTP methods for request simulation
        status_codes (List[int]): HTTP status codes with weighted distribution
    """

    def __init__(self, num_servers: int = 20):
        """
        Initialize the data generator with infrastructure configuration.
        
        Args:
            num_servers (int): Number of servers in the load balancer pool
        """
        self.servers = [f"server-{i:03d}" for i in range(1, num_servers + 1)]
        self.regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        self.request_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.status_codes = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]
        
        # Traffic distribution weights (realistic patterns)
        self.region_weights = [3, 2, 3, 2]  # us-east-1 and eu-west-1 get more traffic
        self.status_weights = [60, 15, 10, 5, 2, 2, 3, 1, 1, 1]  # Most requests succeed
        self.method_weights = [70, 20, 5, 3, 2]  # GET requests dominate
        
        logger.info(f"Initialized data generator with {len(self.servers)} servers across {len(self.regions)} regions")

    def generate_request_log(self, num_requests: int = 5000, time_span_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Generate synthetic request-level logs for load balancer analysis.
        
        Creates realistic request logs with temporal patterns, regional distribution,
        and occasional anomalies to simulate real-world load balancer traffic.
        
        Args:
            num_requests (int): Number of request log entries to generate
            time_span_hours (int): Time span for request distribution
            
        Returns:
            List[Dict[str, Any]]: List of request log dictionaries containing:
                - timestamp: Request timestamp
                - server_id: Target server identifier
                - region: Deployment region
                - request_method: HTTP method
                - status_code: Response status code
                - response_time_ms: Response latency in milliseconds
                - retry_rate: Client retry probability
                - bytes_sent: Response payload size
                - client_ip: Simulated client IP address
                - user_agent: Client user agent string
        """
        logs = []
        base_time = datetime.datetime.now()

        logger.info(f"Generating {num_requests} request logs over {time_span_hours} hours")

        for _ in range(num_requests):
            # Generate timestamp with realistic temporal distribution
            timestamp = base_time - datetime.timedelta(
                seconds=random.randint(0, time_span_hours * 3600)
            )

            # Simulate response time with normal distribution and anomaly spikes
            response_time = max(1, int(random.normalvariate(150, 50)))
            
            # Inject performance anomalies (0.5% of requests)
            if random.random() < 0.005:
                response_time *= random.randint(3, 8)  # Simulate backend congestion

            # Select status code with realistic distribution
            status_code = random.choices(self.status_codes, weights=self.status_weights)[0]
            
            # Higher retry rates for failed requests
            if status_code >= 400:
                retry_rate = round(min(1, max(0, random.betavariate(5, 15))), 3)
            else:
                retry_rate = round(min(1, max(0, random.betavariate(2, 30))), 3)

            log_entry = {
                "timestamp": timestamp.isoformat(),
                "server_id": random.choice(self.servers),
                "region": random.choices(self.regions, weights=self.region_weights)[0],
                "request_method": random.choices(self.request_methods, weights=self.method_weights)[0],
                "status_code": status_code,
                "response_time_ms": response_time,
                "retry_rate": retry_rate,
                "bytes_sent": random.randint(500, 50000),
                "client_ip": ".".join(str(random.randint(1, 254)) for _ in range(4)),
                "user_agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "curl/7.68.0",
                    "PostmanRuntime/7.28.4",
                    "Python/requests 2.28.0",
                    "Go-http-client/1.1"
                ])
            }
            logs.append(log_entry)

        logger.info(f"Generated {len(logs)} request log entries")
        return logs

    def generate_server_metrics(self, duration_hours: int = 24, interval_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Generate synthetic server performance and health metrics.
        
        Creates realistic server metrics including resource utilization, network traffic,
        and health check results with correlated patterns and occasional failures.
        
        Args:
            duration_hours (int): Time span for metrics generation
            interval_minutes (int): Interval between metric snapshots
            
        Returns:
            List[Dict[str, Any]]: List of server metric dictionaries containing:
                - timestamp: Metric collection timestamp
                - server_id: Server identifier
                - cpu_usage_percent: CPU utilization percentage
                - memory_usage_percent: Memory utilization percentage
                - disk_usage_percent: Disk utilization percentage
                - network_in_mbps: Inbound network traffic
                - network_out_mbps: Outbound network traffic
                - active_connections: Number of active connections
                - requests_per_second: Request throughput
                - backend_health_failures: Health check failure count
        """
        metrics = []
        base_time = datetime.datetime.now()
        intervals = duration_hours * (60 // interval_minutes)

        logger.info(f"Generating server metrics for {len(self.servers)} servers over {duration_hours} hours")

        for server in self.servers:
            # Each server has a baseline load pattern
            server_baseline = random.uniform(0.2, 0.8)
            
            for interval in range(intervals):
                timestamp = base_time - datetime.timedelta(minutes=interval * interval_minutes)
                
                # Add some temporal variation (higher load during business hours)
                hour = timestamp.hour
                temporal_factor = 1.0
                if 9 <= hour <= 17:  # Business hours
                    temporal_factor = 1.3
                elif 22 <= hour or hour <= 6:  # Night hours
                    temporal_factor = 0.7

                # Calculate correlated resource usage
                base_load = min(0.95, server_baseline * temporal_factor + random.normalvariate(0, 0.1))
                
                # CPU and memory are correlated
                cpu_usage = round(min(100, max(0, base_load * 100 + random.normalvariate(0, 8))), 2)
                memory_usage = round(min(100, max(0, base_load * 85 + random.normalvariate(0, 10))), 2)
                
                # Network traffic correlates with load
                network_factor = base_load * random.uniform(0.8, 1.2)
                network_in = round(network_factor * 800 + random.normalvariate(0, 100), 2)
                network_out = round(network_factor * 600 + random.normalvariate(0, 80), 2)

                metric = {
                    "timestamp": timestamp.isoformat(),
                    "server_id": server,
                    "cpu_usage_percent": cpu_usage,
                    "memory_usage_percent": memory_usage,
                    "disk_usage_percent": round(random.uniform(35, 85), 2),
                    "network_in_mbps": max(0, network_in),
                    "network_out_mbps": max(0, network_out),
                    "active_connections": int(max(0, base_load * 600 + random.normalvariate(0, 50))),
                    "requests_per_second": int(max(0, base_load * 120 + random.normalvariate(0, 20))),
                    "backend_health_failures": random.choices([0, 1, 2, 3], weights=[85, 10, 4, 1])[0]
                }
                metrics.append(metric)

        logger.info(f"Generated {len(metrics)} server metric entries")
        return metrics

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Save structured data to CSV format.
        
        Args:
            data (List[Dict[str, Any]]): Data to save
            filename (str): Output CSV filename
        """
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(data)} records to {filename}")
        except Exception as e:
            logger.error(f"Error saving CSV file {filename}: {e}")
            raise

    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Save structured data to JSON format.
        
        Args:
            data (List[Dict[str, Any]]): Data to save
            filename (str): Output JSON filename
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(data)} records to {filename}")
        except Exception as e:
            logger.error(f"Error saving JSON file {filename}: {e}")
            raise

    def generate_complete_dataset(self, 
                                num_requests: int = 10000, 
                                duration_hours: int = 24,
                                output_dir: str = "../data/") -> Dict[str, str]:
        """
        Generate a complete dataset including both request logs and server metrics.
        
        Args:
            num_requests (int): Number of request log entries
            duration_hours (int): Time span for data generation
            output_dir (str): Directory for output files
            
        Returns:
            Dict[str, str]: Dictionary with paths to generated files
        """
        logger.info(f"Generating complete dataset: {num_requests} requests over {duration_hours} hours")
        
        # Generate request logs
        request_logs = self.generate_request_log(num_requests, duration_hours)
        request_file = f"{output_dir}request_logs.csv"
        self.save_to_csv(request_logs, request_file)
        
        # Generate server metrics
        server_metrics = self.generate_server_metrics(duration_hours)
        metrics_file = f"{output_dir}server_metrics.csv"
        self.save_to_csv(server_metrics, metrics_file)
        
        # Generate test subset
        test_logs = self.generate_request_log(num_requests // 10, 1)
        test_file = f"{output_dir}test_metrics.csv"
        self.save_to_csv(test_logs, test_file)
        
        files = {
            "request_logs": request_file,
            "server_metrics": metrics_file,
            "test_metrics": test_file
        }
        
        logger.info("Complete dataset generation finished")
        return files


def main():
    """Main execution function for standalone data generation."""
    generator = LoadBalancerDataGenerator()

    print("\n" + "="*60)
    print("LOAD BALANCER SYNTHETIC DATA GENERATION")
    print("="*60)

    try:
        # Generate comprehensive dataset
        files = generator.generate_complete_dataset(
            num_requests=15000,
            duration_hours=24,
            output_dir=""
        )
        
        print("\nGenerated Files:")
        for file_type, filepath in files.items():
            print(f"  {file_type}: {filepath}")
        
        print("\n" + "="*60)
        print("Data generation complete. Ready for analytics processing.")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error in data generation: {e}")
        raise


if __name__ == "__main__":
    main()
