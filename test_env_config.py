#!/usr/bin/env python3
"""
Test Database Connection with Environment Variables
"""

import sys
import os
from dotenv import load_dotenv

# Add source path
sys.path.append(os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'src'))

# Load environment variables
load_dotenv('load-balancer-observability-dashboard/.env')

def test_environment_config():
    """Test environment variable loading."""
    print("🔍 TESTING ENVIRONMENT CONFIGURATION")
    print("=" * 50)
    
    # Test environment variables
    env_vars = {
        'DB_SERVER': os.getenv('DB_SERVER'),
        'DB_DATABASE': os.getenv('DB_DATABASE'),
        'DB_AUTH_TYPE': os.getenv('DB_AUTH_TYPE'),
        'DB_USERNAME': os.getenv('DB_USERNAME'),
        'DB_DRIVER': os.getenv('DB_DRIVER'),
        'DATA_DIRECTORY': os.getenv('DATA_DIRECTORY')
    }
    
    print("Environment Variables:")
    for key, value in env_vars.items():
        status = "✅" if value and value != 'YOUR_SERVER_NAME' else "❌"
        display_value = value if key != 'DB_USERNAME' else f"{value[:3]}***{value[-3:]}" if value else "Not set"
        print(f"  {status} {key}: {display_value}")
    
    return all(value and value != 'YOUR_SERVER_NAME' for value in env_vars.values())

def test_database_connection():
    """Test database connection with environment variables."""
    print("\n🔍 TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        from sql_injector import SQLDataWarehouse
        
        # Initialize with environment variables
        warehouse = SQLDataWarehouse()
        
        # Test connection
        if warehouse.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_pipeline():
    """Test the complete pipeline with environment variables."""
    print("\n🔍 TESTING COMPLETE PIPELINE")
    print("=" * 50)
    
    try:
        from observability_orchestrator import ObservabilityOrchestrator
        
        # Initialize with environment variables
        orchestrator = ObservabilityOrchestrator()
        
        # Run small test
        results = orchestrator.run_complete_pipeline(
            num_requests=10,
            duration_hours=1,
            store_in_database=True  # Test database storage
        )
        
        if results.get('success'):
            print("✅ Complete pipeline test successful!")
            print(f"  Steps completed: {len(results.get('steps_completed', []))}")
            if 'analytics_summary' in results:
                summary = results['analytics_summary']
                print(f"  Requests processed: {summary.get('total_requests', 0)}")
            return True
        else:
            print("❌ Complete pipeline test failed!")
            print(f"  Errors: {results.get('errors', [])}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 ENVIRONMENT-BASED CONFIGURATION TEST")
    print("=" * 60)
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    if not env_ok:
        print("\n❌ Environment configuration incomplete!")
        print("Please configure your .env file with actual credentials.")
        return
    
    # Test database connection
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n❌ Database connection failed!")
        print("Please check your database server and credentials.")
        return
    
    # Test complete pipeline
    pipeline_ok = test_pipeline()
    
    if pipeline_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("The system is ready for production use.")
    else:
        print("\n❌ Pipeline test failed!")

if __name__ == "__main__":
    main()
