#!/usr/bin/env python3
"""
Integration Test Suite for Load Balancer Analytics at Hyperscale

This script performs comprehensive testing of all components before Git deployment.
Tests include: imports, database connectivity, data generation, analytics processing,
and file system operations.

Author: Fares Chehidi (fareschehidi@gmail.com)
"""

import os
import sys
import traceback
from datetime import datetime

def print_test_header(test_name):
    """Print formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print('='*60)

def print_result(test_name, success, message="", details=""):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   📝 {message}")
    if details:
        print(f"   🔍 Details: {details}")

def test_python_environment():
    """Test Python environment and basic imports."""
    print_test_header("Python Environment")
    
    # Test Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_result("Python Version", True, f"Python {python_version}")
    
    # Test essential imports
    essential_modules = [
        ('os', 'Operating system interface'),
        ('sys', 'System-specific parameters'),
        ('datetime', 'Date and time handling'),
        ('json', 'JSON encoder/decoder'),
        ('logging', 'Logging facility'),
        ('time', 'Time-related functions')
    ]
    
    for module_name, description in essential_modules:
        try:
            __import__(module_name)
            print_result(f"Import {module_name}", True, description)
        except ImportError as e:
            print_result(f"Import {module_name}", False, "Import failed", str(e))

def test_data_science_libraries():
    """Test data science and analytics libraries."""
    print_test_header("Data Science Libraries")
    
    libraries = [
        ('pandas', 'Data manipulation and analysis'),
        ('numpy', 'Numerical computing'),
        ('pyodbc', 'ODBC database connectivity'),
        ('scikit-learn', 'Machine learning (if available)')
    ]
    
    for lib_name, description in libraries:
        try:
            __import__(lib_name)
            print_result(f"Import {lib_name}", True, description)
        except ImportError as e:
            if lib_name == 'scikit-learn':
                try:
                    import sklearn
                    print_result(f"Import sklearn", True, description)
                except ImportError:
                    print_result(f"Import {lib_name}", False, "Optional library missing", str(e))
            else:
                print_result(f"Import {lib_name}", False, "Required library missing", str(e))

def test_project_structure():
    """Test project directory structure and file existence."""
    print_test_header("Project Structure")
    
    # Test main project directories
    base_path = os.getcwd()
    
    required_structure = {
        'load-balancer-observability-dashboard': 'Observability dashboard project',
        'load-balancer-retry-prediction': 'ML retry prediction project',
        'assets': 'Project assets and images',
        'PROJECT_OVERVIEW.md': 'Main project documentation'
    }
    
    for item, description in required_structure.items():
        item_path = os.path.join(base_path, item)
        exists = os.path.exists(item_path)
        print_result(f"Structure: {item}", exists, description, item_path if exists else "Missing")
    
    # Test observability dashboard structure
    obs_base = os.path.join(base_path, 'load-balancer-observability-dashboard')
    if os.path.exists(obs_base):
        obs_structure = {
            'src': 'Source code directory',
            'data': 'Data files directory', 
            'config': 'Configuration files',
            'docs': 'Documentation',
            'requirements.txt': 'Python dependencies'
        }
        
        for item, description in obs_structure.items():
            item_path = os.path.join(obs_base, item)
            exists = os.path.exists(item_path)
            print_result(f"Observability: {item}", exists, description)

def test_source_code_imports():
    """Test imports of custom source code modules."""
    print_test_header("Source Code Imports")
    
    # Add observability dashboard to path
    obs_src_path = os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'src')
    if obs_src_path not in sys.path:
        sys.path.insert(0, obs_src_path)
    
    modules_to_test = [
        ('data_generation', 'LoadBalancerDataGenerator'),
        ('dashboard_engine', 'DashboardEngine'), 
        ('sql_injector', 'SQLDataWarehouse'),
        ('observability_orchestrator', 'ObservabilityOrchestrator')
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print_result(f"Module {module_name}", True, f"Contains {class_name}")
            else:
                print_result(f"Module {module_name}", False, f"Missing {class_name}")
        except Exception as e:
            print_result(f"Module {module_name}", False, "Import failed", str(e))

def test_database_configuration():
    """Test database configuration and connectivity."""
    print_test_header("Database Configuration")
    
    try:
        # Test SQL Server driver availability
        import pyodbc
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_drivers:
            print_result("ODBC SQL Server Driver", True, f"Available drivers: {sql_drivers}")
        else:
            print_result("ODBC SQL Server Driver", False, "No SQL Server drivers found")
        
        # Test database schema file
        schema_path = os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'config', 'database_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'TrafficInsights' in content:
                    print_result("Database Schema", True, "TrafficInsights schema found")
                else:
                    print_result("Database Schema", False, "TrafficInsights not found in schema")
        else:
            print_result("Database Schema", False, "Schema file missing")
            
    except ImportError as e:
        print_result("Database Libraries", False, "pyodbc not available", str(e))

def test_data_generation():
    """Test data generation without database dependency."""
    print_test_header("Data Generation (Offline Test)")
    
    try:
        # Add source path
        obs_src_path = os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'src')
        if obs_src_path not in sys.path:
            sys.path.insert(0, obs_src_path)
        
        from data_generation import LoadBalancerDataGenerator
        
        # Test data generator initialization
        generator = LoadBalancerDataGenerator()
        print_result("Data Generator Init", True, "LoadBalancerDataGenerator created")
        
        # Test small data generation
        test_data = generator.generate_request_log(100, 1)
        if len(test_data) == 100:
            print_result("Request Log Generation", True, f"Generated {len(test_data)} records")
        else:
            print_result("Request Log Generation", False, f"Expected 100, got {len(test_data)}")
        
        # Test server metrics generation
        server_data = generator.generate_server_metrics(1)
        if len(server_data) > 0:
            print_result("Server Metrics Generation", True, f"Generated {len(server_data)} records")
        else:
            print_result("Server Metrics Generation", False, "No server metrics generated")
            
    except Exception as e:
        print_result("Data Generation", False, "Data generation failed", str(e))
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")

def test_analytics_engine():
    """Test analytics engine without database dependency."""
    print_test_header("Analytics Engine (Offline Test)")
    
    try:
        obs_src_path = os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'src')
        if obs_src_path not in sys.path:
            sys.path.insert(0, obs_src_path)
        
        from dashboard_engine import DashboardEngine
        
        # Test analytics engine initialization
        engine = DashboardEngine()
        print_result("Analytics Engine Init", True, "DashboardEngine created")
        
        # Test with sample data
        import tempfile
        import pandas as pd
        
        # Create sample data
        sample_requests = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'server_id': ['server_001'] * 100,
            'status_code': [200] * 80 + [500] * 20,
            'response_time_ms': [100] * 100,
            'retry_rate': [0.1] * 100
        })
        
        sample_metrics = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=10, freq='10min'),
            'server_id': ['server_001'] * 10,
            'cpu_usage_percent': [50.0] * 10,
            'memory_usage_percent': [60.0] * 10
        })
        
        # Save to temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
            sample_requests.to_csv(f1.name, index=False)
            request_file = f1.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            sample_metrics.to_csv(f2.name, index=False)
            metrics_file = f2.name
        
        # Test loading data
        engine.load_data(request_file, metrics_file)
        print_result("Data Loading", True, "Sample data loaded successfully")
        
        # Clean up temporary files
        os.unlink(request_file)
        os.unlink(metrics_file)
        
    except Exception as e:
        print_result("Analytics Engine", False, "Analytics engine failed", str(e))
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")

def test_file_permissions():
    """Test file system permissions and data directory access."""
    print_test_header("File System Permissions")
    
    test_dirs = [
        'load-balancer-observability-dashboard/data',
        'load-balancer-retry-prediction/data'
    ]
    
    for test_dir in test_dirs:
        dir_path = os.path.join(os.getcwd(), test_dir)
        
        try:
            # Test directory creation
            os.makedirs(dir_path, exist_ok=True)
            print_result(f"Directory Access: {test_dir}", True, "Directory created/accessible")
            
            # Test file write
            test_file = os.path.join(dir_path, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test data')
            
            # Test file read
            with open(test_file, 'r') as f:
                content = f.read()
            
            if content == 'test data':
                print_result(f"File I/O: {test_dir}", True, "Read/write operations successful")
            else:
                print_result(f"File I/O: {test_dir}", False, "File content mismatch")
            
            # Clean up
            os.remove(test_file)
            
        except Exception as e:
            print_result(f"File System: {test_dir}", False, "File system error", str(e))

def run_all_tests():
    """Run complete test suite."""
    print(f"""
    🚀 LOAD BALANCER ANALYTICS INTEGRATION TEST SUITE
    ================================================
    Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Working Directory: {os.getcwd()}
    Python Version: {sys.version}
    
    This test suite validates all components before Git deployment.
    """)
    
    # Run all test categories
    test_functions = [
        test_python_environment,
        test_data_science_libraries,
        test_project_structure,
        test_source_code_imports,
        test_database_configuration,
        test_file_permissions,
        test_data_generation,
        test_analytics_engine
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print_result(f"Test Suite: {test_func.__name__}", False, "Test function failed", str(e))
    
    print(f"\n{'='*60}")
    print("🏁 INTEGRATION TESTING COMPLETED")
    print('='*60)
    print(f"Next Steps:")
    print(f"1. ✅ Review all test results above")
    print(f"2. 🔧 Fix any FAILED tests before Git push")
    print(f"3. 🔄 Re-run tests until all pass")
    print(f"4. 📦 Ready for Git deployment when all tests pass")
    print('='*60)

if __name__ == "__main__":
    run_all_tests()
