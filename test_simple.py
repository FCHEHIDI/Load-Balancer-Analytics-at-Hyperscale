#!/usr/bin/env python3
"""
Simple Pipeline Test
"""

import sys
import os
import logging

# Add source path
sys.path.append(os.path.join(os.getcwd(), 'load-balancer-observability-dashboard', 'src'))

from observability_orchestrator import ObservabilityOrchestrator

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise

def main():
    """Test the pipeline results structure."""
    print("🔍 TESTING PIPELINE RESULTS STRUCTURE")
    print("=" * 50)
    
    try:
        orchestrator = ObservabilityOrchestrator()
        
        print("Running pipeline test...")
        results = orchestrator.run_complete_pipeline(
            num_requests=50,
            duration_hours=1,
            store_in_database=False
        )
        
        print(f"Pipeline success: {results.get('success', 'unknown')}")
        print(f"Steps completed: {len(results.get('steps_completed', []))}")
        print(f"Data files keys: {list(results.get('data_files', {}).keys())}")
        print(f"Analytics summary available: {'analytics_summary' in results}")
        
        if "analytics_summary" in results:
            summary = results["analytics_summary"]
            print(f"  Total requests: {summary.get('total_requests', 'N/A')}")
            print(f"  Error rate: {summary.get('error_rate', 'N/A')}%")
        
        if results.get('success'):
            print("✅ All components working correctly!")
        else:
            print("❌ Pipeline had issues - check logs")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
