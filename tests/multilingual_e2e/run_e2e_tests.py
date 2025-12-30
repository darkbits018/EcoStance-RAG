"""
Comprehensive test runner for multilingual E2E testing
Executes all test suites and generates detailed reports
"""

import sys
import os
import pytest
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from tests.multilingual_e2e.utils.reporting_utils import MultilingualTestReporter, PerformanceMetricsCollector
from tests.multilingual_e2e.utils.cleanup_utils import get_cleanup_manager, emergency_cleanup


class MultilingualE2ETestRunner:
    """Main test runner for multilingual E2E testing."""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.reporter = MultilingualTestReporter(str(self.output_dir))
        self.performance_collector = PerformanceMetricsCollector()
        self.cleanup_manager = get_cleanup_manager()
    
    def run_all_tests(self, test_categories: Optional[List[str]] = None, 
                     include_property_tests: bool = True,
                     include_performance_tests: bool = True,
                     max_examples: int = 100) -> int:
        """Run all multilingual E2E tests."""
        
        print("🚀 Starting Multilingual E2E Test Suite")
        print("=" * 50)
        
        self.reporter.start_test_run()
        
        # Add environment info
        env_info = self._collect_environment_info()
        self.reporter.add_environment_info(env_info)
        
        # Define test categories and their corresponding test files
        all_test_categories = {
            "config": "tests/multilingual_e2e/test_config.py",
            "document_processing": "tests/multilingual_e2e/test_document_processing.py",
            "embedding_validation": "tests/multilingual_e2e/test_embedding_validation.py",
            "search_retrieval": "tests/multilingual_e2e/test_search_retrieval.py",
            "rag_pipeline": "tests/multilingual_e2e/test_rag_pipeline.py",
            "agent_conversation": "tests/multilingual_e2e/test_agent_conversation.py",
            "api_integration": "tests/multilingual_e2e/test_api_integration.py",
            "performance_benchmarks": "tests/multilingual_e2e/test_performance_benchmarks.py",
            "semantic_accuracy": "tests/multilingual_e2e/test_semantic_accuracy.py"
        }
        
        # Filter test categories if specified
        if test_categories:
            test_files = [all_test_categories[cat] for cat in test_categories if cat in all_test_categories]
        else:
            test_files = list(all_test_categories.values())
        
        # Build pytest arguments
        pytest_args = [
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "-x",  # Stop on first failure (optional)
            f"--maxfail=5",  # Stop after 5 failures
        ]
        
        # Add markers for selective testing
        markers = []
        if not include_property_tests:
            markers.append("not property_test")
        if not include_performance_tests:
            markers.append("not performance")
        
        if markers:
            pytest_args.extend(["-m", " and ".join(markers)])
        
        # Set hypothesis configuration via environment variables
        if include_property_tests:
            import os
            os.environ["HYPOTHESIS_MAX_EXAMPLES"] = str(max_examples)
            os.environ["HYPOTHESIS_DEADLINE"] = "60000"
        
        # Add test files
        pytest_args.extend(test_files)
        
        print(f"📋 Running tests: {', '.join(test_categories or ['all'])}")
        print(f"🔧 Property tests: {'enabled' if include_property_tests else 'disabled'}")
        print(f"⚡ Performance tests: {'enabled' if include_performance_tests else 'disabled'}")
        print()
        
        try:
            # Run pytest
            exit_code = pytest.main(pytest_args)
            
            # Collect results (this would be enhanced with pytest hooks in a real implementation)
            self._collect_test_results(exit_code)
            
            return exit_code
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return 1
        
        finally:
            # Always cleanup and generate reports
            self._cleanup_and_report()
    
    def run_quick_smoke_tests(self) -> int:
        """Run a quick subset of tests for smoke testing."""
        print("🔥 Running Quick Smoke Tests")
        print("=" * 30)
        
        smoke_test_categories = ["config", "document_processing", "api_integration"]
        
        return self.run_all_tests(
            test_categories=smoke_test_categories,
            include_property_tests=False,
            include_performance_tests=False
        )
    
    def run_property_tests_only(self, max_examples: int = 100) -> int:
        """Run only property-based tests."""
        print("🧪 Running Property-Based Tests Only")
        print("=" * 35)
        
        # Set hypothesis configuration
        import os
        os.environ["HYPOTHESIS_MAX_EXAMPLES"] = str(max_examples)
        os.environ["HYPOTHESIS_DEADLINE"] = "60000"
        
        pytest_args = [
            "-v",
            "-m", "property_test",
            "tests/multilingual_e2e/"
        ]
        
        self.reporter.start_test_run()
        
        try:
            exit_code = pytest.main(pytest_args)
            self._collect_test_results(exit_code)
            return exit_code
        
        finally:
            self._cleanup_and_report()
    
    def run_performance_tests_only(self) -> int:
        """Run only performance benchmark tests."""
        print("⚡ Running Performance Tests Only")
        print("=" * 32)
        
        pytest_args = [
            "-v",
            "-m", "performance",
            "tests/multilingual_e2e/test_performance_benchmarks.py"
        ]
        
        self.reporter.start_test_run()
        
        try:
            exit_code = pytest.main(pytest_args)
            self._collect_test_results(exit_code)
            return exit_code
        
        finally:
            self._cleanup_and_report()
    
    def _collect_environment_info(self) -> dict:
        """Collect environment information for the report."""
        import platform
        import sys
        
        try:
            from app.config.multilingual_app_config import get_multilingual_config_info
            multilingual_config = get_multilingual_config_info()
        except ImportError:
            multilingual_config = {"error": "Could not import multilingual config"}
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "multilingual_config": multilingual_config,
            "test_environment": {
                "pdf_file": "logistics-multilanguage.pdf",
                "test_tenant": "test_multilingual_tenant"
            }
        }
    
    def _collect_test_results(self, exit_code: int):
        """Collect test results (simplified - would use pytest hooks in real implementation)."""
        # This is a simplified version - in a real implementation, 
        # you'd use pytest hooks to collect detailed results
        
        if exit_code == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code: {exit_code}")
        
        # Add basic result info
        self.reporter.add_test_result("overall", "test_execution", {
            "passed": exit_code == 0,
            "failed": exit_code != 0,
            "exit_code": exit_code
        })
    
    def _cleanup_and_report(self):
        """Cleanup resources and generate reports."""
        print("\n🧹 Cleaning up test resources...")
        
        # Cleanup test resources
        cleanup_results = self.cleanup_manager.cleanup_all()
        print(f"   Cleaned up {cleanup_results['summary']['total_successful']} resources")
        
        if cleanup_results['summary']['total_failed'] > 0:
            print(f"   ⚠️  Failed to cleanup {cleanup_results['summary']['total_failed']} resources")
        
        # End test run
        self.reporter.end_test_run()
        
        # Generate summary
        summary = self.reporter.generate_summary()
        
        print("\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        # Save reports
        print("\n📄 Generating reports...")
        
        json_report = self.reporter.save_report()
        print(f"   JSON Report: {json_report}")
        
        html_report = self.reporter.generate_html_report()
        print(f"   HTML Report: {html_report}")
        
        print(f"\n🎉 Test run completed! Reports saved to: {self.output_dir}")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Multilingual E2E Test Runner")
    
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["config", "document_processing", "embedding_validation", 
                "search_retrieval", "rag_pipeline", "agent_conversation", 
                "api_integration", "performance_benchmarks", "semantic_accuracy"],
        help="Test categories to run (default: all)"
    )
    
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run quick smoke tests only"
    )
    
    parser.add_argument(
        "--property-only",
        action="store_true",
        help="Run property-based tests only"
    )
    
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run performance tests only"
    )
    
    parser.add_argument(
        "--no-property",
        action="store_true",
        help="Skip property-based tests"
    )
    
    parser.add_argument(
        "--no-performance",
        action="store_true",
        help="Skip performance tests"
    )
    
    parser.add_argument(
        "--max-examples",
        type=int,
        default=100,
        help="Maximum examples for property tests (default: 100)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="test_results",
        help="Output directory for test reports (default: test_results)"
    )
    
    parser.add_argument(
        "--emergency-cleanup",
        action="store_true",
        help="Perform emergency cleanup of test resources and exit"
    )
    
    args = parser.parse_args()
    
    # Handle emergency cleanup
    if args.emergency_cleanup:
        print("🚨 Performing emergency cleanup...")
        cleanup_results = emergency_cleanup()
        print(f"Emergency cleanup completed: {cleanup_results}")
        return 0
    
    # Create test runner
    runner = MultilingualE2ETestRunner(args.output_dir)
    
    # Run appropriate test suite
    if args.smoke:
        exit_code = runner.run_quick_smoke_tests()
    elif args.property_only:
        exit_code = runner.run_property_tests_only(args.max_examples)
    elif args.performance_only:
        exit_code = runner.run_performance_tests_only()
    else:
        exit_code = runner.run_all_tests(
            test_categories=args.categories,
            include_property_tests=not args.no_property,
            include_performance_tests=not args.no_performance,
            max_examples=args.max_examples
        )
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())