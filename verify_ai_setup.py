#!/usr/bin/env python3
"""
Script to verify AI/ML library setup.
This script checks if all required AI/ML libraries for the tax law application
are properly installed and working.
"""

import sys
from app.ai.utils import run_all_tests, check_library_imports

def main():
    """
    Main function to verify AI/ML library setup.
    """
    print("Verifying AI/ML library setup...")
    
    # Check library imports first
    import_status = check_library_imports()
    all_imports_successful = all(import_status.values())
    
    if not all_imports_successful:
        failed_imports = [lib for lib, status in import_status.items() if not status]
        print(f"ERROR: Some libraries failed to import: {', '.join(failed_imports)}")
        print("Please make sure they are installed correctly.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run all tests
    print("\nRunning functionality tests...")
    test_results = run_all_tests()
    
    # Check if all tests passed
    flat_results = []
    for result in test_results.values():
        if isinstance(result, dict):
            flat_results.extend(result.values())
        else:
            flat_results.append(result)
    
    all_tests_passed = all(flat_results)
    
    if all_tests_passed:
        print("\n✅ SUCCESS: All AI/ML libraries are properly installed and working!")
        print("\nYou can now proceed with the development of the tax law application.")
    else:
        print("\n❌ ERROR: Some tests failed. Please check the logs above for details.")
        print("Make sure your environment is properly set up.")
        sys.exit(1)

if __name__ == "__main__":
    main()
