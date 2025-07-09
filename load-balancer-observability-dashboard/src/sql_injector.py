"""
SQL Server Integration Module for Load Balancer Analytics

This module provides comprehensive SQL Server integration for the load balancer
observability platform, including table management, data insertion, and
analytics report storage with enterprise-grade performance and reliability.

Key Features:
- Automated table creation and schema management
- Batch data insertion with transaction safety
- Analytics report storage and retrieval
- Data retention and cleanup policies
- Connection pooling and error handling
- Performance optimization with proper indexing
- Secure credential management with environment variables

Author: Fares Chehidi (fareschehidi28@gmail.com)
"""

import pyodbc
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLDataWarehouse:
    """
    Enterprise SQL Server integration for load balancer telemetry data.
    
    This class manages the complete data warehouse lifecycle including schema creation,
    data insertion, analytics storage, and maintenance operations for load balancer
    observability data. Uses secure environment variables for credential management.
    
    Attributes:
        connection_string (str): SQL Server connection configuration
        batch_size (int): Number of records to insert in each batch
        retry_attempts (int): Number of connection retry attempts
    """

    def __init__(self, 
                 server: str = None,
                 database: str = None, 
                 batch_size: int = 1000,
                 retry_attempts: int = 3):
        """
        Initialize SQL data warehouse connection using environment variables.
        
        Uses secure credential management with environment variables from .env file.
        Falls back to provided parameters if environment variables are not set.
        
        Args:
            server (str): SQL Server instance name (overrides DB_SERVER env var)
            database (str): Target database name (overrides DB_DATABASE env var)
            batch_size (int): Batch size for bulk operations
            retry_attempts (int): Number of retry attempts for failed operations
        """
        # Load database configuration from environment variables
        self.server = server or os.getenv('DB_SERVER', 'YOUR_SERVER_NAME')
        self.database = database or os.getenv('DB_DATABASE', 'TrafficInsights')
        self.username = os.getenv('DB_USERNAME', '')
        self.password = os.getenv('DB_PASSWORD', '')
        self.auth_type = os.getenv('DB_AUTH_TYPE', 'Windows Authentication')
        self.driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        self.connection_timeout = int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
        
        # Build connection string based on authentication type
        if self.auth_type == 'Windows Authentication':
            self.connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                "Trusted_Connection=yes;"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                f"Connection Timeout={self.connection_timeout};"
            )
        else:
            self.connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                f"Connection Timeout={self.connection_timeout};"
            )
        
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        
        # Log initialization (without revealing credentials)
        logger.info(f"Initialized SQL data warehouse connection to {self.server}/{self.database}")
        if self.server == 'YOUR_SERVER_NAME':
            logger.warning("Using default server name. Please configure DB_SERVER environment variable.")

    def test_connection(self) -> bool:
        """
        Test database connectivity and permissions.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def create_database_schema(self) -> None:
        """
        Create complete database schema with tables, indexes, and constraints.
        
        Creates optimized tables for request logs, server metrics, and analytics
        reports with proper indexing for dashboard performance.
        
        Raises:
            Exception: If schema creation fails
        """
        table_definitions = [
            """
            IF OBJECT_ID('RequestLogs') IS NULL
            CREATE TABLE RequestLogs (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                timestamp DATETIME2(3) NOT NULL,
                server_id VARCHAR(50) NOT NULL,
                region VARCHAR(50) NOT NULL,
                request_method VARCHAR(10) NOT NULL,
                status_code INT NOT NULL,
                response_time_ms INT NOT NULL,
                retry_rate FLOAT NOT NULL,
                bytes_sent BIGINT NOT NULL,
                client_ip VARCHAR(45),
                user_agent VARCHAR(500),
                created_at DATETIME2(3) DEFAULT GETDATE(),
                
                INDEX IX_RequestLogs_Timestamp NONCLUSTERED (timestamp),
                INDEX IX_RequestLogs_Server NONCLUSTERED (server_id),
                INDEX IX_RequestLogs_Region NONCLUSTERED (region),
                INDEX IX_RequestLogs_Status NONCLUSTERED (status_code),
                INDEX IX_RequestLogs_Performance NONCLUSTERED (response_time_ms, retry_rate)
            )
            """,
            """
            IF OBJECT_ID('ServerMetrics') IS NULL
            CREATE TABLE ServerMetrics (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                timestamp DATETIME2(3) NOT NULL,
                server_id VARCHAR(50) NOT NULL,
                cpu_usage_percent FLOAT NOT NULL,
                memory_usage_percent FLOAT NOT NULL,
                disk_usage_percent FLOAT NOT NULL,
                network_in_mbps FLOAT NOT NULL,
                network_out_mbps FLOAT NOT NULL,
                active_connections INT NOT NULL,
                requests_per_second INT NOT NULL,
                backend_health_failures INT NOT NULL,
                created_at DATETIME2(3) DEFAULT GETDATE(),
                
                INDEX IX_ServerMetrics_Timestamp NONCLUSTERED (timestamp),
                INDEX IX_ServerMetrics_Server NONCLUSTERED (server_id),
                INDEX IX_ServerMetrics_Performance NONCLUSTERED (cpu_usage_percent, memory_usage_percent),
                INDEX IX_ServerMetrics_Health NONCLUSTERED (backend_health_failures)
            )
            """,
            """
            IF OBJECT_ID('AnalyticsReports') IS NULL
            CREATE TABLE AnalyticsReports (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                report_timestamp DATETIME2(3) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                report_data NVARCHAR(MAX) NOT NULL,
                processing_time_ms INT,
                record_count INT,
                created_at DATETIME2(3) DEFAULT GETDATE(),
                
                INDEX IX_AnalyticsReports_Timestamp NONCLUSTERED (report_timestamp),
                INDEX IX_AnalyticsReports_Type NONCLUSTERED (report_type)
            )
            """,
            """
            IF OBJECT_ID('DataQualityMetrics') IS NULL
            CREATE TABLE DataQualityMetrics (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                check_timestamp DATETIME2(3) DEFAULT GETDATE(),
                table_name VARCHAR(50) NOT NULL,
                total_records INT NOT NULL,
                null_values INT,
                duplicate_records INT,
                data_freshness_hours FLOAT,
                quality_score FLOAT,
                
                INDEX IX_DataQuality_Timestamp NONCLUSTERED (check_timestamp),
                INDEX IX_DataQuality_Table NONCLUSTERED (table_name)
            )
            """
        ]

        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                for table_sql in table_definitions:
                    cursor.execute(table_sql)
                    
                conn.commit()
                logger.info("Database schema created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            raise

    def insert_request_logs(self, records: List[Dict[str, Any]]) -> int:
        """
        Insert request log records with batch processing and error handling.
        
        Args:
            records (List[Dict[str, Any]]): List of request log dictionaries
            
        Returns:
            int: Number of records successfully inserted
            
        Raises:
            Exception: If insertion fails after all retry attempts
        """
        if not records:
            logger.warning("No request log records to insert")
            return 0

        insert_sql = """
        INSERT INTO RequestLogs (timestamp, server_id, region, request_method, status_code,
                               response_time_ms, retry_rate, bytes_sent, client_ip, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        return self._batch_insert(insert_sql, records, "request logs", self._prepare_request_log_row)

    def insert_server_metrics(self, records: List[Dict[str, Any]]) -> int:
        """
        Insert server metrics records with batch processing and validation.
        
        Args:
            records (List[Dict[str, Any]]): List of server metrics dictionaries
            
        Returns:
            int: Number of records successfully inserted
            
        Raises:
            Exception: If insertion fails after all retry attempts
        """
        if not records:
            logger.warning("No server metrics records to insert")
            return 0

        insert_sql = """
        INSERT INTO ServerMetrics (timestamp, server_id, cpu_usage_percent, memory_usage_percent,
                                 disk_usage_percent, network_in_mbps, network_out_mbps, 
                                 active_connections, requests_per_second, backend_health_failures)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        return self._batch_insert(insert_sql, records, "server metrics", self._prepare_server_metrics_row)

    def store_analytics_report(self, report_data: Dict[str, Any], 
                              report_type: str = "comprehensive",
                              processing_time_ms: Optional[int] = None) -> bool:
        """
        Store analytics report with metadata tracking.
        
        Args:
            report_data (Dict[str, Any]): Analytics report data
            report_type (str): Type of report (comprehensive, summary, etc.)
            processing_time_ms (Optional[int]): Processing time in milliseconds
            
        Returns:
            bool: True if storage successful, False otherwise
        """
        insert_sql = """
        INSERT INTO AnalyticsReports (report_timestamp, report_type, report_data, 
                                    processing_time_ms, record_count)
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            # Calculate record count from report
            record_count = 0
            if 'request_kpis' in report_data:
                record_count = report_data['request_kpis'].get('total_requests', 0)
            
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (
                    datetime.now(),
                    report_type,
                    json.dumps(report_data, default=str, indent=2),
                    processing_time_ms,
                    record_count
                ))
                conn.commit()
                
            logger.info(f"Analytics report stored successfully: {report_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store analytics report: {e}")
            return False

    def cleanup_old_data(self, retention_days: int = 90) -> Dict[str, int]:
        """
        Clean up old data based on retention policy.
        
        Args:
            retention_days (int): Number of days to retain data
            
        Returns:
            Dict[str, int]: Number of records deleted from each table
        """
        cleanup_results = {}
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleanup_tables = {
            "RequestLogs": "created_at",
            "ServerMetrics": "created_at", 
            "AnalyticsReports": "created_at",
            "DataQualityMetrics": "check_timestamp"
        }
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                for table, date_column in cleanup_tables.items():
                    delete_sql = f"DELETE FROM {table} WHERE {date_column} < ?"
                    cursor.execute(delete_sql, cutoff_date)
                    deleted_count = cursor.rowcount
                    cleanup_results[table] = deleted_count
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} records from {table}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            raise
            
        return cleanup_results

    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """
        Calculate and return data quality metrics for monitoring.
        
        Returns:
            Dict[str, Any]: Data quality metrics including record counts,
                          freshness, and completeness statistics
        """
        metrics = {}
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Request logs metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(CASE WHEN server_id IS NULL THEN 1 END) as null_server_ids,
                        COUNT(CASE WHEN response_time_ms <= 0 THEN 1 END) as invalid_response_times,
                        DATEDIFF(hour, MAX(timestamp), GETDATE()) as hours_since_last_record
                    FROM RequestLogs
                """)
                
                result = cursor.fetchone()
                metrics['request_logs'] = {
                    'total_records': result[0],
                    'null_server_ids': result[1],
                    'invalid_response_times': result[2],
                    'hours_since_last_record': result[3]
                }
                
                # Server metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(CASE WHEN cpu_usage_percent < 0 OR cpu_usage_percent > 100 THEN 1 END) as invalid_cpu,
                        DATEDIFF(hour, MAX(timestamp), GETDATE()) as hours_since_last_record
                    FROM ServerMetrics
                """)
                
                result = cursor.fetchone()
                metrics['server_metrics'] = {
                    'total_records': result[0],
                    'invalid_cpu_values': result[1],
                    'hours_since_last_record': result[2]
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate data quality metrics: {e}")
            
        return metrics

    def _batch_insert(self, insert_sql: str, records: List[Dict[str, Any]], 
                     record_type: str, row_preparer) -> int:
        """
        Perform batch insertion with retry logic and error handling.
        
        Args:
            insert_sql (str): SQL insert statement
            records (List[Dict[str, Any]]): Records to insert
            record_type (str): Type of records for logging
            row_preparer: Function to prepare individual rows
            
        Returns:
            int: Number of records successfully inserted
        """
        total_inserted = 0
        
        for attempt in range(self.retry_attempts):
            try:
                with pyodbc.connect(self.connection_string) as conn:
                    cursor = conn.cursor()
                    
                    # Process in batches
                    for i in range(0, len(records), self.batch_size):
                        batch = records[i:i + self.batch_size]
                        
                        for record in batch:
                            row_data = row_preparer(record)
                            cursor.execute(insert_sql, row_data)
                        
                        total_inserted += len(batch)
                    
                    conn.commit()
                    logger.info(f"Successfully inserted {total_inserted} {record_type} records")
                    return total_inserted
                    
            except Exception as e:
                logger.warning(f"Insert attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Failed to insert {record_type} after {self.retry_attempts} attempts")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return total_inserted

    def _prepare_request_log_row(self, record: Dict[str, Any]) -> tuple:
        """Prepare request log record for database insertion."""
        return (
            record['timestamp'],
            record['server_id'],
            record['region'],
            record['request_method'],
            record['status_code'],
            record['response_time_ms'],
            record['retry_rate'],
            record['bytes_sent'],
            record.get('client_ip', ''),
            record.get('user_agent', '')
        )

    def _prepare_server_metrics_row(self, record: Dict[str, Any]) -> tuple:
        """Prepare server metrics record for database insertion."""
        return (
            record['timestamp'],
            record['server_id'],
            record['cpu_usage_percent'],
            record['memory_usage_percent'],
            record['disk_usage_percent'],
            record['network_in_mbps'],
            record['network_out_mbps'],
            record['active_connections'],
            record['requests_per_second'],
            record['backend_health_failures']
        )


def main():
    """Main execution function for standalone database operations."""
    warehouse = SQLDataWarehouse()
    
    # Test connection
    if not warehouse.test_connection():
        logger.error("Database connection failed. Please check configuration.")
        return
    
    # Create schema
    try:
        warehouse.create_database_schema()
        logger.info("Database schema ready")
    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        return
    
    # Load and insert data if available
    try:
        # Try to load CSV files
        request_logs_df = pd.read_csv("../data/request_logs.csv")
        server_metrics_df = pd.read_csv("../data/server_metrics.csv")
        
        # Insert data
        warehouse.insert_request_logs(request_logs_df.to_dict("records"))
        warehouse.insert_server_metrics(server_metrics_df.to_dict("records"))
        
        # Get data quality metrics
        quality_metrics = warehouse.get_data_quality_metrics()
        logger.info(f"Data quality metrics: {quality_metrics}")
        
    except FileNotFoundError:
        logger.warning("CSV data files not found. Run data_generation.py first to generate test data.")
    except Exception as e:
        logger.error(f"Data loading failed: {e}")


if __name__ == "__main__":
    main()
