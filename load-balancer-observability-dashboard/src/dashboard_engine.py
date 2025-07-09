"""
Load Balancer Analytics Dashboard Engine

This module provides comprehensive analytics processing for load balancer telemetry data.
It processes request logs and server metrics to compute KPIs, detect anomalies, and
generate reports suitable for visualization in Power BI dashboards.

Key Features:
- Request-level performance analytics (latency, throughput, error rates)
- Server health monitoring and resource utilization tracking
- Traffic pattern analysis and trend detection
- Anomaly detection for proactive alerting
- Comprehensive reporting for business intelligence

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardEngine:
    """
    Backend analytics engine for load balancer performance visualization.
    
    This class processes traffic logs and server metrics to extract business-relevant 
    insights including performance KPIs, anomaly detection, and traffic pattern analysis.
    
    Attributes:
        request_logs_df (pd.DataFrame): Processed request log data
        server_metrics_df (pd.DataFrame): Processed server metrics data
    """

    def __init__(self):
        """Initialize the dashboard engine with empty data containers."""
        self.request_logs_df: Optional[pd.DataFrame] = None
        self.server_metrics_df: Optional[pd.DataFrame] = None
        logger.info("Dashboard engine initialized")

    def load_data(self, request_logs_path: str, server_metrics_path: str) -> None:
        """
        Load CSV data files into pandas dataframes for analysis.
        
        Args:
            request_logs_path (str): Path to request logs CSV file
            server_metrics_path (str): Path to server metrics CSV file
            
        Raises:
            FileNotFoundError: If either data file cannot be found
            pd.errors.EmptyDataError: If data files are empty
        """
        try:
            self.request_logs_df = pd.read_csv(request_logs_path, parse_dates=["timestamp"])
            self.server_metrics_df = pd.read_csv(server_metrics_path, parse_dates=["timestamp"])
            
            logger.info(f"Loaded {len(self.request_logs_df)} request logs and {len(self.server_metrics_df)} server metrics")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def compute_request_kpis(self) -> Dict[str, Any]:
        """
        Analyze request-level logs for volume, latency, errors, retries, and traffic distribution.
        
        Returns:
            Dict[str, Any]: Dictionary containing request-level KPIs including:
                - Total requests and requests per second
                - Response time statistics (mean, P95, P99)
                - Error rate and retry statistics
                - Traffic distribution by region, method, and status code
                
        Raises:
            ValueError: If request logs data is not loaded
        """
        if self.request_logs_df is None:
            raise ValueError("Request logs data not loaded. Call load_data() first.")
            
        df = self.request_logs_df.copy()

        # Calculate time span for rate calculations
        total_time_seconds = (df['timestamp'].max() - df['timestamp'].min()).total_seconds()
        total_time_seconds = max(total_time_seconds, 1)  # Avoid division by zero

        kpis = {
            # Volume metrics
            "total_requests": len(df),
            "requests_per_second": round(len(df) / total_time_seconds, 2),
            
            # Latency metrics
            "average_response_time_ms": round(df['response_time_ms'].mean(), 2),
            "p95_response_time_ms": round(df['response_time_ms'].quantile(0.95), 2),
            "p99_response_time_ms": round(df['response_time_ms'].quantile(0.99), 2),
            
            # Error and retry metrics
            "error_rate_percent": round((df['status_code'] >= 400).mean() * 100, 2),
            "retry_rate_avg": round(df['retry_rate'].mean(), 3),
            "retry_rate_p95": round(df['retry_rate'].quantile(0.95), 3),
            
            # Data transfer metrics
            "total_bytes_transferred": int(df['bytes_sent'].sum()),
            "average_bytes_per_request": round(df['bytes_sent'].mean(), 2),
            
            # Distribution metrics
            "region_distribution": df['region'].value_counts().to_dict(),
            "method_distribution": df['request_method'].value_counts().to_dict(),
            "status_code_distribution": df['status_code'].value_counts().to_dict()
        }

        logger.info(f"Computed request KPIs: {kpis['total_requests']} requests, {kpis['error_rate_percent']}% error rate")
        return kpis

    def compute_server_kpis(self) -> Dict[str, Any]:
        """
        Analyze server metrics for performance, saturation, and backend health.
        
        Returns:
            Dict[str, Any]: Dictionary containing server-level KPIs including:
                - CPU and memory utilization statistics
                - Network throughput metrics
                - Health check failure tracking
                - Server-specific performance breakdowns
                
        Raises:
            ValueError: If server metrics data is not loaded
        """
        if self.server_metrics_df is None:
            raise ValueError("Server metrics data not loaded. Call load_data() first.")
            
        df = self.server_metrics_df.copy()

        kpis = {
            # Resource utilization
            "average_cpu_usage": round(df['cpu_usage_percent'].mean(), 2),
            "max_cpu_usage": round(df['cpu_usage_percent'].max(), 2),
            "average_memory_usage": round(df['memory_usage_percent'].mean(), 2),
            "max_memory_usage": round(df['memory_usage_percent'].max(), 2),
            
            # Connection and request metrics
            "total_active_connections": int(df['active_connections'].sum()),
            "average_requests_per_second": round(df['requests_per_second'].mean(), 2),
            
            # Health metrics
            "backend_health_failures_total": int(df['backend_health_failures'].sum()),
            "backend_health_failures_by_server": df.groupby('server_id')['backend_health_failures'].sum().to_dict(),
            
            # Network metrics (convert to GB/hour)
            "total_network_in_gb": round((df['network_in_mbps'].sum() * 3600) / (8 * 1024), 2),
            "total_network_out_gb": round((df['network_out_mbps'].sum() * 3600) / (8 * 1024), 2)
        }

        # Identify overloaded servers (threshold: 80% utilization)
        server_util = df.groupby("server_id").agg({
            "cpu_usage_percent": "mean",
            "memory_usage_percent": "mean",
            "requests_per_second": "mean"
        }).round(2)

        kpis["high_cpu_servers"] = server_util[server_util["cpu_usage_percent"] > 80].index.tolist()
        kpis["high_memory_servers"] = server_util[server_util["memory_usage_percent"] > 80].index.tolist()
        kpis["server_utilization"] = server_util.to_dict("index")

        logger.info(f"Computed server KPIs: {len(kpis['high_cpu_servers'])} high CPU servers, {kpis['backend_health_failures_total']} health failures")
        return kpis

    def compute_traffic_patterns(self) -> Dict[str, Any]:
        """
        Analyze temporal traffic behavior and latency trends.
        
        Returns:
            Dict[str, Any]: Dictionary containing traffic pattern analysis including:
                - Hourly and daily traffic volume distributions
                - Latency trends by time of day
                - Peak traffic identification
                
        Raises:
            ValueError: If request logs data is not loaded
        """
        if self.request_logs_df is None:
            raise ValueError("Request logs data not loaded. Call load_data() first.")
            
        df = self.request_logs_df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()

        patterns = {
            "hourly_traffic_volume": df.groupby("hour").size().to_dict(),
            "daily_traffic_volume": df.groupby("day_of_week").size().to_dict(),
            "hourly_avg_latency": df.groupby("hour")["response_time_ms"].mean().round(2).to_dict(),
            "top_latency_hours": df.groupby("hour")["response_time_ms"].mean().nlargest(5).round(2).to_dict()
        }

        logger.info("Computed traffic patterns and temporal trends")
        return patterns

    def detect_anomalies(self) -> Dict[str, Any]:
        """
        Detect abnormal latency patterns and health failure trends.
        
        Uses statistical methods to identify outliers and potential issues:
        - Response time anomalies (mean + 3 standard deviations)
        - Error rate spikes by hour
        - Server health check failures above threshold
        
        Returns:
            Dict[str, Any]: Dictionary containing anomaly detection results
            
        Raises:
            ValueError: If required data is not loaded
        """
        if self.request_logs_df is None or self.server_metrics_df is None:
            raise ValueError("Both request logs and server metrics data must be loaded")
            
        anomalies = {}

        df_req = self.request_logs_df.copy()
        df_srv = self.server_metrics_df.copy()

        # Response time anomaly threshold: mean + 3 standard deviations
        threshold_rt = df_req['response_time_ms'].mean() + 3 * df_req['response_time_ms'].std()
        anomalies["slow_request_threshold_ms"] = round(threshold_rt, 2)
        anomalies["slow_request_count"] = int((df_req['response_time_ms'] > threshold_rt).sum())

        # Error spikes per hour (2x normal error rate)
        hourly_errors = df_req.groupby(df_req['timestamp'].dt.hour).apply(
            lambda x: (x['status_code'] >= 400).mean() * 100
        )
        error_spike_hours = hourly_errors[hourly_errors > hourly_errors.mean() * 2].round(2).to_dict()
        anomalies["error_spike_hours"] = error_spike_hours

        # Backend health check failures (threshold: 5 failures)
        anomalies["server_health_failures_above_5"] = df_srv[df_srv["backend_health_failures"] > 5]["server_id"].unique().tolist()

        logger.info(f"Detected {anomalies['slow_request_count']} slow requests and {len(anomalies['server_health_failures_above_5'])} unhealthy servers")
        return anomalies

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a complete analytics report combining all computed metrics.
        
        Returns:
            Dict[str, Any]: Comprehensive report containing:
                - Request-level KPIs
                - Server performance metrics
                - Traffic pattern analysis
                - Anomaly detection results
                - Report metadata
                
        Raises:
            ValueError: If required data is not loaded
        """
        if self.request_logs_df is None or self.server_metrics_df is None:
            raise ValueError("Both request logs and server metrics data must be loaded")
            
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "request_log_entries": len(self.request_logs_df),
                "server_metric_entries": len(self.server_metrics_df),
                "time_range": {
                    "start": self.request_logs_df['timestamp'].min().isoformat(),
                    "end": self.request_logs_df['timestamp'].max().isoformat()
                }
            },
            "request_kpis": self.compute_request_kpis(),
            "server_kpis": self.compute_server_kpis(),
            "traffic_patterns": self.compute_traffic_patterns(),
            "anomalies": self.detect_anomalies()
        }

        logger.info("Generated comprehensive analytics report")
        return report

    def save_report(self, report: Dict[str, Any], filename: str = "analytics_report.json") -> None:
        """
        Export analytics report to a JSON file.
        
        Args:
            report (Dict[str, Any]): Report dictionary to save
            filename (str): Output filename (default: "analytics_report.json")
        """
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Analytics report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise


def main():
    """Main execution function for standalone usage."""
    engine = DashboardEngine()

    try:
        # Load data files
        engine.load_data("../data/request_logs.csv", "../data/server_metrics.csv")
        
        # Generate comprehensive report
        report = engine.generate_comprehensive_report()
        
        # Save report
        engine.save_report(report, "../data/analytics_report.json")

        # Print summary
        print("\n" + "="*50)
        print("LOAD BALANCER ANALYTICS SUMMARY")
        print("="*50)
        print(f"Total Requests: {report['request_kpis']['total_requests']:,}")
        print(f"Average Response Time: {report['request_kpis']['average_response_time_ms']:.2f}ms")
        print(f"P95 Response Time: {report['request_kpis']['p95_response_time_ms']:.2f}ms")
        print(f"Error Rate: {report['request_kpis']['error_rate_percent']:.2f}%")
        print(f"Average Retry Rate: {report['request_kpis']['retry_rate_avg']:.3f}")
        print(f"Backend Health Failures: {report['server_kpis']['backend_health_failures_total']}")
        print(f"High CPU Servers: {len(report['server_kpis']['high_cpu_servers'])}")
        print(f"Anomalous Slow Requests: {report['anomalies']['slow_request_count']}")
        print("="*50)
        
    except FileNotFoundError:
        logger.error("Data files not found. Please run data_generation.py first to generate test data.")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
