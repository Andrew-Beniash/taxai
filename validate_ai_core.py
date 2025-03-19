#!/usr/bin/env python3
"""
Validation script for the AI core processing system.
This script runs tests for the AI engine, query processor, and response caching.
"""

import os
import sys
import unittest
import time
import logging
import argparse
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_core_validation.log')
    ]
)
logger = logging.getLogger(__name__)


def discover_tests(test_patterns: List[str] = None) -> unittest.TestSuite:
    """
    Discover all test cases to run.
    
    Args:
        test_patterns: Optional list of test name patterns to run
        
    Returns:
        TestSuite of discovered tests
    """
    if not test_patterns:
        # Run all tests if no patterns specified
        logger.info("Discovering all AI core tests...")
        return unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    
    # Create a test suite to hold all the tests
    suite = unittest.TestSuite()
    
    # Find tests that match the specified patterns
    for pattern in test_patterns:
        logger.info(f"Discovering tests with pattern: {pattern}")
        discovered = unittest.defaultTestLoader.discover('tests', pattern=f'test_{pattern}*.py')
        suite.addTests(discovered)
    
    return suite


def run_tests(suite: unittest.TestSuite) -> Tuple[int, int]:
    """
    Run the test suite and return results.
    
    Args:
        suite: The test suite to run
        
    Returns:
        Tuple of (tests run, tests failed)
    """
    # Create a test runner with verbosity level 2 (more detailed output)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests and get the results
    result = runner.run(suite)
    
    return result.testsRun, len(result.failures) + len(result.errors)


def main():
    """
    Main function to run the AI core validation.
    """
    parser = argparse.ArgumentParser(description='Validate the AI core processing system')
    parser.add_argument('--tests', nargs='*', help='Specific test patterns to run (e.g., ai_core query_processor)')
    parser.add_argument('--skip-cache', action='store_true', help='Skip cache tests')
    args = parser.parse_args()
    
    # Print header for the validation
    print("\n" + "="*80)
    print(" "*30 + "AI CORE VALIDATION")
    print("="*80 + "\n")
    
    start_time = time.time()
    logger.info("Starting AI core validation...")
    
    # Process test patterns
    test_patterns = args.tests
    
    # If skipping cache tests, filter out cache-related patterns
    if args.skip_cache and not test_patterns:
        test_patterns = ['ai_core', 'query_processor', 'irs_validation']
    
    # Discover tests
    suite = discover_tests(test_patterns)
    
    # Run tests
    tests_run, tests_failed = run_tests(suite)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "="*80)
    print(f"VALIDATION SUMMARY:")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_run - tests_failed}")
    print(f"Tests failed: {tests_failed}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print("="*80 + "\n")
    
    if tests_failed > 0:
        logger.error(f"Validation failed with {tests_failed} failed tests")
        sys.exit(1)
    else:
        logger.info("AI core validation completed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
