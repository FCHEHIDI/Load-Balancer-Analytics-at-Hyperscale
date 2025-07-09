"""
Observability Orchestrator for Load Balancer Analytics

This module coordinates the complete observability pipeline including data generation,
analytics processing, SQL data warehousing, and dashboard integration. It provides
a unified interface for managing the entire load balancer monitoring workflow.

Key Features:
- End-to-end pipeline orchestration
- Error handling and retry logic
- Performance monitoring and logging
- Configurable execution workflows
- Health checking and validation
- Secure credential management with environment variables

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_generation import LoadBalancerDataGenerator
from dashboard_engine import DashboardEngine
from sql_injector import SQLDataWarehouse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObservabilityOrchestrator:
    """
    Main orchestrator for the load balancer observability pipeline.
    
    This class coordinates data generation, analytics processing, and database
    storage to provide a complete observability solution for load balancer
    environments.
    
    Attributes:
        generator (LoadBalancerDataGenerator): Data generation component
        engine (DashboardEngine): Analytics processing component
        warehouse (SQLDataWarehouse): Database storage component
    """

    def __init__(self, 
                 sql_server: str = None,
                 database: str = None,
                 data_dir: str = None):
        """
        Initialize the observability orchestrator using environment variables.
        
        Uses secure credential management with environment variables from .env file.
        Falls back to provided parameters if environment variables are not set.
        
        Args:
            sql_server (str): SQL Server instance name (overrides DB_SERVER env var)
            database (str): Target database name (overrides DB_DATABASE env var)
            data_dir (str): Directory for data file storage (overrides DATA_DIRECTORY env var)
        """
        # Load configuration from environment variables
        self.data_dir = data_dir or os.getenv('DATA_DIRECTORY', '../data/')
        
        # Initialize components with environment-based configuration
        self.generator = LoadBalancerDataGenerator()
        self.engine = DashboardEngine()
        self.warehouse = SQLDataWarehouse(server=sql_server, database=database)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info("Observability orchestrator initialized with environment configuration")

    def validate_infrastructure(self, check_database: bool = True) -> bool:
        """
        Validate that all required infrastructure components are available.
        
        Args:
            check_database (bool): Whether to validate database connectivity
            
        Returns:
            bool: True if all components are ready, False otherwise
        """
        logger.info("Validating infrastructure components...")
        
        # Test database connectivity if required
        if check_database:
            if not self.warehouse.test_connection():
                logger.error("Database connection validation failed")
                return False
        else:
            logger.info("Skipping database connectivity validation")
        
        # Test data directory access
        try:
            test_file = os.path.join(self.data_dir, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            logger.error(f"Data directory access validation failed: {e}")
            return False
        
        logger.info("Infrastructure validation completed successfully")
        return True

    def setup_database_schema(self) -> bool:
        """
        Initialize database schema and required tables.
        
        Returns:
            bool: True if schema setup successful, False otherwise
        """
        try:
            logger.info("Setting up database schema...")
            self.warehouse.create_database_schema()
            logger.info("Database schema setup completed")
            return True
        except Exception as e:
            logger.error(f"Database schema setup failed: {e}")
            return False

    def generate_synthetic_data(self, 
                               num_requests: int = 15000,
                               duration_hours: int = 24) -> Dict[str, str]:
        """
        Generate comprehensive synthetic telemetry data.
        
        Args:
            num_requests (int): Number of request log entries to generate
            duration_hours (int): Time span for data generation
            
        Returns:
            Dict[str, str]: Dictionary mapping data types to file paths
        """
        logger.info(f"Generating synthetic data: {num_requests} requests over {duration_hours} hours")
        
        start_time = time.time()
        
        try:
            # Generate request logs
            request_logs = self.generator.generate_request_log(num_requests, duration_hours)
            request_file = os.path.join(self.data_dir, "request_logs.csv")
            self.generator.save_to_csv(request_logs, request_file)
            
            # Generate server metrics
            server_metrics = self.generator.generate_server_metrics(duration_hours)
            metrics_file = os.path.join(self.data_dir, "server_metrics.csv")
            self.generator.save_to_csv(server_metrics, metrics_file)
            
            # Generate test subset for validation
            test_logs = self.generator.generate_request_log(num_requests // 10, 1)
            test_file = os.path.join(self.data_dir, "test_metrics.csv")
            self.generator.save_to_csv(test_logs, test_file)
            
            generation_time = time.time() - start_time
            logger.info(f"Data generation completed in {generation_time:.2f} seconds")
            
            return {
                "request_logs": request_file,
                "server_metrics": metrics_file,
                "test_metrics": test_file
            }
            
        except Exception as e:
            logger.error(f"Data generation failed: {e}")
            raise

    def process_analytics(self, data_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Process telemetry data to generate analytics insights.
        
        Args:
            data_files (Dict[str, str]): Dictionary mapping data types to file paths
            
        Returns:
            Dict[str, Any]: Comprehensive analytics report
        """
        logger.info("Processing analytics from generated data...")
        
        start_time = time.time()
        
        try:
            # Load data into analytics engine
            self.engine.load_data(
                data_files["request_logs"],
                data_files["server_metrics"]
            )
            
            # Generate comprehensive report
            analytics_report = self.engine.generate_comprehensive_report()
            
            # Save report to file
            report_file = os.path.join(self.data_dir, "analytics_report.json")
            self.engine.save_report(analytics_report, report_file)
            
            processing_time = time.time() - start_time
            analytics_report["processing_metadata"] = {
                "processing_time_seconds": round(processing_time, 2),
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Analytics processing completed in {processing_time:.2f} seconds")
            return analytics_report
            
        except Exception as e:
            logger.error(f"Analytics processing failed: {e}")
            raise

    def store_data_warehouse(self, data_files: Dict[str, str], 
                           analytics_report: Dict[str, Any]) -> bool:
        """
        Store all data in SQL Server data warehouse.
        
        Args:
            data_files (Dict[str, str]): Dictionary mapping data types to file paths
            analytics_report (Dict[str, Any]): Analytics report to store
            
        Returns:
            bool: True if storage successful, False otherwise
        """
        logger.info("Storing data in SQL Server data warehouse...")
        
        try:
            import pandas as pd
            
            # Load and insert request logs
            request_logs_df = pd.read_csv(data_files["request_logs"])
            inserted_requests = self.warehouse.insert_request_logs(
                request_logs_df.to_dict("records")
            )
            
            # Load and insert server metrics
            server_metrics_df = pd.read_csv(data_files["server_metrics"])
            inserted_metrics = self.warehouse.insert_server_metrics(
                server_metrics_df.to_dict("records")
            )
            
            # Store analytics report
            processing_time = analytics_report.get("processing_metadata", {}).get("processing_time_seconds")
            processing_time_ms = int(processing_time * 1000) if processing_time else None
            
            report_stored = self.warehouse.store_analytics_report(
                analytics_report,
                "comprehensive",
                processing_time_ms
            )
            
            logger.info(f"Data warehouse storage completed: {inserted_requests} requests, {inserted_metrics} metrics")
            return report_stored
            
        except Exception as e:
            logger.error(f"Data warehouse storage failed: {e}")
            return False

    def cleanup_old_data(self, retention_days: int = 90) -> Dict[str, int]:
        """
        Clean up old data from the warehouse based on retention policy.
        
        Args:
            retention_days (int): Number of days to retain data
            
        Returns:
            Dict[str, int]: Number of records cleaned up from each table
        """
        logger.info(f"Cleaning up data older than {retention_days} days...")
        
        try:
            cleanup_results = self.warehouse.cleanup_old_data(retention_days)
            total_cleaned = sum(cleanup_results.values())
            logger.info(f"Cleanup completed: {total_cleaned} total records removed")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            return {}

    def run_complete_pipeline(self, 
                            num_requests: int = 15000,
                            duration_hours: int = 24,
                            store_in_database: bool = True) -> Dict[str, Any]:
        """
        Execute the complete observability pipeline from data generation to storage.
        
        Args:
            num_requests (int): Number of request log entries to generate
            duration_hours (int): Time span for data generation
            store_in_database (bool): Whether to store data in SQL Server
            
        Returns:
            Dict[str, Any]: Pipeline execution results and metrics
        """
        logger.info("Starting complete observability pipeline execution")
        pipeline_start = time.time()
        
        results = {
            "pipeline_start": datetime.now().isoformat(),
            "configuration": {
                "num_requests": num_requests,
                "duration_hours": duration_hours,
                "store_in_database": store_in_database
            },
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Step 1: Validate infrastructure
            if not self.validate_infrastructure(check_database=store_in_database):
                raise Exception("Infrastructure validation failed")
            results["steps_completed"].append("infrastructure_validation")
            
            # Step 2: Setup database schema
            if store_in_database:
                if not self.setup_database_schema():
                    raise Exception("Database schema setup failed")
                results["steps_completed"].append("database_schema_setup")
            
            # Step 3: Generate synthetic data
            data_files = self.generate_synthetic_data(num_requests, duration_hours)
            results["data_files"] = data_files
            results["steps_completed"].append("data_generation")
            
            # Step 4: Process analytics
            analytics_report = self.process_analytics(data_files)
            results["analytics_summary"] = {
                "total_requests": analytics_report["request_kpis"]["total_requests"],
                "error_rate": analytics_report["request_kpis"]["error_rate_percent"],
                "avg_response_time": analytics_report["request_kpis"]["average_response_time_ms"],
                "anomalies_detected": analytics_report["anomalies"]["slow_request_count"]
            }
            results["steps_completed"].append("analytics_processing")
            
            # Step 5: Store in data warehouse
            if store_in_database:
                warehouse_success = self.store_data_warehouse(data_files, analytics_report)
                if warehouse_success:
                    results["steps_completed"].append("data_warehouse_storage")
                else:
                    results["errors"].append("Data warehouse storage failed")
            
            # Calculate total execution time
            pipeline_duration = time.time() - pipeline_start
            results["pipeline_duration_seconds"] = round(pipeline_duration, 2)
            results["pipeline_end"] = datetime.now().isoformat()
            results["success"] = True
            
            logger.info(f"Pipeline completed successfully in {pipeline_duration:.2f} seconds")
            
        except Exception as e:
            pipeline_duration = time.time() - pipeline_start
            results["pipeline_duration_seconds"] = round(pipeline_duration, 2)
            results["pipeline_end"] = datetime.now().isoformat()
            results["success"] = False
            results["errors"].append(str(e))
            logger.error(f"Pipeline failed after {pipeline_duration:.2f} seconds: {e}")
            
        return results

    def print_pipeline_summary(self, results: Dict[str, Any]) -> None:
        """
        Print a formatted summary of pipeline execution results.
        
        Args:
            results (Dict[str, Any]): Pipeline execution results
        """
        print("\n" + "="*70)
        print("LOAD BALANCER OBSERVABILITY PIPELINE SUMMARY")
        print("="*70)
        
        print(f"Pipeline Status: {'SUCCESS' if results['success'] else 'FAILED'}")
        print(f"Execution Time: {results['pipeline_duration_seconds']} seconds")
        print(f"Started: {results['pipeline_start']}")
        print(f"Completed: {results['pipeline_end']}")
        
        print(f"\nSteps Completed ({len(results['steps_completed'])}):")
        for step in results["steps_completed"]:
            print(f"  ✓ {step.replace('_', ' ').title()}")
        
        if results.get("analytics_summary"):
            summary = results["analytics_summary"]
            print(f"\nAnalytics Summary:")
            print(f"  Total Requests: {summary['total_requests']:,}")
            print(f"  Error Rate: {summary['error_rate']:.2f}%")
            print(f"  Avg Response Time: {summary['avg_response_time']:.2f}ms")
            print(f"  Anomalies Detected: {summary['anomalies_detected']}")
        
        if results.get("errors"):
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  ✗ {error}")
        
        print("="*70)


def main():
    """Main execution function for standalone pipeline orchestration."""
    orchestrator = ObservabilityOrchestrator()
    
    # Run complete pipeline
    results = orchestrator.run_complete_pipeline(
        num_requests=20000,
        duration_hours=24,
        store_in_database=True
    )
    
    # Print summary
    orchestrator.print_pipeline_summary(results)
    
    # Optional: Clean up old data
    if results["success"]:
        cleanup_results = orchestrator.cleanup_old_data(retention_days=30)
        if cleanup_results:
            print(f"\nData Cleanup: {sum(cleanup_results.values())} old records removed")


if __name__ == "__main__":
    main()
