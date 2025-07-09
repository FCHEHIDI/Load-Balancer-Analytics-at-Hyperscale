"""
Basic setup validation script for the Load Balancer Retry Prediction project.

This script validates that all components are properly configured and ready for use.

Author: Fares Chehidi (fareschehidi@gmail.com)
"""

import os
import sys
import json
from pathlib import Path

def check_project_structure():
    """Verify that all required project directories and files exist."""
    print("🔍 Checking project structure...")
    
    required_dirs = [
        'notebooks',
        'src',
        'src/utils',
        'models',
        'data',
        'docs'
    ]
    
    required_files = [
        'README.md',
        'requirements.txt',
        'LICENSE',
        'notebooks/retry_prediction_analysis.ipynb',
        'src/prediction_api.py',
        'src/utils/data_processing.py',
        'src/utils/model_utils.py',
        'data/telemetry_data.csv',
        'docs/deployment_guide.md',
        'docs/api_documentation.md',
        'docs/business_case.md'
    ]
    
    # Check directories
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    # Check files
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Project structure is complete!")
    return True

def check_data_files():
    """Verify that data files exist and are accessible."""
    print("\n🔍 Checking data files...")
    
    data_file = 'data/telemetry_data.csv'
    if not os.path.exists(data_file):
        print(f"❌ Data file missing: {data_file}")
        return False
    
    # Check file size
    file_size = os.path.getsize(data_file)
    if file_size == 0:
        print(f"❌ Data file is empty: {data_file}")
        return False
    
    print(f"✅ Data file exists ({file_size:,} bytes)")
    return True

def check_dependencies():
    """Check if key dependencies can be imported."""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'pandas',
        'numpy',
        'sklearn',
        'matplotlib',
        'seaborn',
        'joblib',
        'flask'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def generate_project_summary():
    """Generate a summary of the project structure and status."""
    print("\n📋 Project Summary:")
    print("=" * 50)
    
    # Count files by type
    file_counts = {
        'Python files': 0,
        'Jupyter notebooks': 0,
        'Documentation': 0,
        'Data files': 0,
        'Other files': 0
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_counts['Python files'] += 1
            elif file.endswith('.ipynb'):
                file_counts['Jupyter notebooks'] += 1
            elif file.endswith(('.md', '.txt', '.rst')):
                file_counts['Documentation'] += 1
            elif file.endswith(('.csv', '.json', '.pkl')):
                file_counts['Data files'] += 1
            else:
                file_counts['Other files'] += 1
    
    for category, count in file_counts.items():
        print(f"  {category}: {count}")
    
    print("\n📁 Key Components:")
    print("  • Machine Learning Pipeline: notebooks/retry_prediction_analysis.ipynb")
    print("  • Production API: src/prediction_api.py")
    print("  • Data Processing: src/utils/data_processing.py")
    print("  • Model Management: src/utils/model_utils.py")
    print("  • Business Documentation: docs/business_case.md")
    print("  • Deployment Guide: docs/deployment_guide.md")

def main():
    """Main validation function."""
    print("🚀 Load Balancer Retry Prediction - Setup Validation")
    print("=" * 60)
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run all checks
    structure_ok = check_project_structure()
    data_ok = check_data_files()
    deps_ok = check_dependencies()
    
    # Generate summary
    generate_project_summary()
    
    # Final status
    print("\n" + "=" * 60)
    if structure_ok and data_ok and deps_ok:
        print("🎉 All checks passed! Project is ready for use.")
        print("\nNext steps:")
        print("1. Open notebooks/retry_prediction_analysis.ipynb in Jupyter")
        print("2. Run all cells to train the model")
        print("3. Start the API with: python src/prediction_api.py")
    else:
        print("⚠️  Some issues found. Please address them before proceeding.")
    
    print(f"\nProject Author: Fares Chehidi (fareschehidi@gmail.com)")

if __name__ == "__main__":
    main()
