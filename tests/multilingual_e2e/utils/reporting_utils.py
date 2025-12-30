"""
Test reporting and metrics collection utilities for multilingual E2E testing
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics


class MultilingualTestReporter:
    """Generate comprehensive test reports for multilingual E2E testing."""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = {
            "test_run_info": {
                "start_time": None,
                "end_time": None,
                "duration_seconds": 0,
                "test_framework": "pytest",
                "multilingual_e2e_version": "1.0.0"
            },
            "environment_info": {},
            "test_categories": {
                "document_processing": [],
                "embedding_validation": [],
                "search_retrieval": [],
                "rag_pipeline": [],
                "agent_conversation": [],
                "api_integration": [],
                "performance_benchmarks": [],
                "semantic_accuracy": []
            },
            "property_tests": [],
            "performance_metrics": {},
            "summary": {}
        }
    
    def start_test_run(self):
        """Mark the start of test run."""
        self.test_results["test_run_info"]["start_time"] = datetime.now().isoformat()
    
    def end_test_run(self):
        """Mark the end of test run and calculate duration."""
        end_time = datetime.now()
        self.test_results["test_run_info"]["end_time"] = end_time.isoformat()
        
        if self.test_results["test_run_info"]["start_time"]:
            start_time = datetime.fromisoformat(self.test_results["test_run_info"]["start_time"])
            duration = (end_time - start_time).total_seconds()
            self.test_results["test_run_info"]["duration_seconds"] = duration
    
    def add_environment_info(self, env_info: Dict[str, Any]):
        """Add environment information to the report."""
        self.test_results["environment_info"].update(env_info)
    
    def add_test_result(self, category: str, test_name: str, result: Dict[str, Any]):
        """Add a test result to the appropriate category."""
        if category in self.test_results["test_categories"]:
            test_entry = {
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            self.test_results["test_categories"][category].append(test_entry)
    
    def add_property_test_result(self, property_name: str, result: Dict[str, Any]):
        """Add a property test result."""
        property_entry = {
            "property_name": property_name,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        self.test_results["property_tests"].append(property_entry)
    
    def add_performance_metrics(self, metrics: Dict[str, Any]):
        """Add performance metrics."""
        self.test_results["performance_metrics"].update(metrics)
    
    def generate_summary(self):
        """Generate test run summary."""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "property_tests": len(self.test_results["property_tests"]),
            "categories_tested": 0,
            "performance_metrics_collected": len(self.test_results["performance_metrics"]),
            "success_rate": 0.0
        }
        
        # Count tests by category
        for category, tests in self.test_results["test_categories"].items():
            if tests:
                summary["categories_tested"] += 1
                
            for test in tests:
                summary["total_tests"] += 1
                result = test["result"]
                
                if result.get("passed", False):
                    summary["passed_tests"] += 1
                elif result.get("failed", False):
                    summary["failed_tests"] += 1
                elif result.get("skipped", False):
                    summary["skipped_tests"] += 1
        
        # Count property tests
        for prop_test in self.test_results["property_tests"]:
            summary["total_tests"] += 1
            result = prop_test["result"]
            
            if result.get("passed", False):
                summary["passed_tests"] += 1
            elif result.get("failed", False):
                summary["failed_tests"] += 1
        
        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = (summary["passed_tests"] / summary["total_tests"]) * 100
        
        self.test_results["summary"] = summary
        return summary
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """Save the test report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multilingual_e2e_report_{timestamp}.json"
        
        report_path = self.output_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        return str(report_path)
    
    def generate_html_report(self, filename: Optional[str] = None) -> str:
        """Generate HTML report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multilingual_e2e_report_{timestamp}.html"
        
        report_path = self.output_dir / filename
        
        html_content = self._generate_html_content()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        summary = self.test_results["summary"]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multilingual E2E Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric h3 {{ margin: 0; color: #2c3e50; }}
        .metric .value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .category {{ margin: 20px 0; }}
        .category h3 {{ background-color: #34495e; color: white; padding: 10px; margin: 0; }}
        .test-result {{ padding: 10px; border-left: 4px solid #ccc; margin: 5px 0; }}
        .passed {{ border-left-color: #27ae60; background-color: #d5f4e6; }}
        .failed {{ border-left-color: #e74c3c; background-color: #fdf2f2; }}
        .skipped {{ border-left-color: #f39c12; background-color: #fef9e7; }}
        .performance {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Multilingual E2E Test Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Duration:</strong> {self.test_results['test_run_info']['duration_seconds']:.2f} seconds</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="value">{summary['total_tests']}</div>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <div class="value" style="color: #27ae60;">{summary['passed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <div class="value" style="color: #e74c3c;">{summary['failed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="value">{summary['success_rate']:.1f}%</div>
        </div>
    </div>
"""
        
        # Add test categories
        for category, tests in self.test_results["test_categories"].items():
            if tests:
                html += f"""
    <div class="category">
        <h3>{category.replace('_', ' ').title()}</h3>
"""
                for test in tests:
                    result = test["result"]
                    status = "passed" if result.get("passed") else "failed" if result.get("failed") else "skipped"
                    html += f"""
        <div class="test-result {status}">
            <strong>{test['test_name']}</strong><br>
            <small>{test['timestamp']}</small>
            {self._format_test_details(result)}
        </div>
"""
                html += "    </div>\n"
        
        # Add performance metrics
        if self.test_results["performance_metrics"]:
            html += """
    <div class="performance">
        <h3>Performance Metrics</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
"""
            for metric, value in self.test_results["performance_metrics"].items():
                html += f"            <tr><td>{metric}</td><td>{value}</td></tr>\n"
            
            html += """
        </table>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def _format_test_details(self, result: Dict[str, Any]) -> str:
        """Format test result details for HTML."""
        details = []
        
        if "duration_ms" in result:
            details.append(f"Duration: {result['duration_ms']}ms")
        
        if "performance_ratio" in result:
            details.append(f"Performance: {result['performance_ratio']:.2f}")
        
        if "error" in result:
            details.append(f"Error: {result['error']}")
        
        if details:
            return "<br><small>" + " | ".join(details) + "</small>"
        
        return ""


class PerformanceMetricsCollector:
    """Collect and analyze performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "document_processing": [],
            "embedding_generation": [],
            "search_queries": [],
            "agent_responses": [],
            "concurrent_operations": []
        }
    
    def add_document_processing_metric(self, file_size_mb: float, processing_time_seconds: float):
        """Add document processing performance metric."""
        self.metrics["document_processing"].append({
            "file_size_mb": file_size_mb,
            "processing_time_seconds": processing_time_seconds,
            "mb_per_second": file_size_mb / processing_time_seconds if processing_time_seconds > 0 else 0
        })
    
    def add_embedding_generation_metric(self, blocks_count: int, processing_time_seconds: float):
        """Add embedding generation performance metric."""
        blocks_per_minute = (blocks_count / processing_time_seconds) * 60 if processing_time_seconds > 0 else 0
        
        self.metrics["embedding_generation"].append({
            "blocks_count": blocks_count,
            "processing_time_seconds": processing_time_seconds,
            "blocks_per_minute": blocks_per_minute
        })
    
    def add_search_query_metric(self, query: str, response_time_ms: int, results_count: int):
        """Add search query performance metric."""
        self.metrics["search_queries"].append({
            "query": query[:50] + "..." if len(query) > 50 else query,
            "response_time_ms": response_time_ms,
            "results_count": results_count
        })
    
    def add_agent_response_metric(self, message: str, response_time_ms: int, language: str):
        """Add agent response performance metric."""
        self.metrics["agent_responses"].append({
            "message": message[:50] + "..." if len(message) > 50 else message,
            "response_time_ms": response_time_ms,
            "language": language
        })
    
    def add_concurrent_operation_metric(self, operation_type: str, concurrent_count: int, 
                                      baseline_time_ms: int, concurrent_avg_time_ms: int):
        """Add concurrent operation performance metric."""
        degradation_percent = ((concurrent_avg_time_ms - baseline_time_ms) / baseline_time_ms) * 100
        
        self.metrics["concurrent_operations"].append({
            "operation_type": operation_type,
            "concurrent_count": concurrent_count,
            "baseline_time_ms": baseline_time_ms,
            "concurrent_avg_time_ms": concurrent_avg_time_ms,
            "degradation_percent": degradation_percent
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        summary = {}
        
        for category, metrics_list in self.metrics.items():
            if not metrics_list:
                continue
            
            category_summary = {"count": len(metrics_list)}
            
            if category == "document_processing":
                times = [m["processing_time_seconds"] for m in metrics_list]
                category_summary.update({
                    "avg_processing_time_seconds": statistics.mean(times),
                    "max_processing_time_seconds": max(times),
                    "min_processing_time_seconds": min(times)
                })
            
            elif category == "embedding_generation":
                rates = [m["blocks_per_minute"] for m in metrics_list]
                category_summary.update({
                    "avg_blocks_per_minute": statistics.mean(rates),
                    "max_blocks_per_minute": max(rates),
                    "min_blocks_per_minute": min(rates)
                })
            
            elif category == "search_queries":
                times = [m["response_time_ms"] for m in metrics_list]
                category_summary.update({
                    "avg_response_time_ms": statistics.mean(times),
                    "max_response_time_ms": max(times),
                    "min_response_time_ms": min(times)
                })
            
            elif category == "agent_responses":
                times = [m["response_time_ms"] for m in metrics_list]
                languages = list(set(m["language"] for m in metrics_list))
                category_summary.update({
                    "avg_response_time_ms": statistics.mean(times),
                    "max_response_time_ms": max(times),
                    "min_response_time_ms": min(times),
                    "languages_tested": languages
                })
            
            elif category == "concurrent_operations":
                degradations = [m["degradation_percent"] for m in metrics_list]
                category_summary.update({
                    "avg_degradation_percent": statistics.mean(degradations),
                    "max_degradation_percent": max(degradations),
                    "min_degradation_percent": min(degradations)
                })
            
            summary[category] = category_summary
        
        return summary


class SemanticAccuracyAnalyzer:
    """Analyze semantic accuracy metrics."""
    
    def __init__(self):
        self.accuracy_metrics = {
            "language_detection": [],
            "semantic_consistency": [],
            "cross_language_equivalence": [],
            "factual_consistency": []
        }
    
    def add_language_detection_result(self, expected_language: str, detected_language: str, 
                                    confidence: float, is_correct: bool):
        """Add language detection accuracy result."""
        self.accuracy_metrics["language_detection"].append({
            "expected_language": expected_language,
            "detected_language": detected_language,
            "confidence": confidence,
            "is_correct": is_correct
        })
    
    def add_semantic_consistency_result(self, concept: str, language_pair: str, 
                                      overlap_score: float, is_consistent: bool):
        """Add semantic consistency result."""
        self.accuracy_metrics["semantic_consistency"].append({
            "concept": concept,
            "language_pair": language_pair,
            "overlap_score": overlap_score,
            "is_consistent": is_consistent
        })
    
    def get_accuracy_summary(self) -> Dict[str, Any]:
        """Get semantic accuracy summary."""
        summary = {}
        
        # Language detection accuracy
        lang_detection = self.accuracy_metrics["language_detection"]
        if lang_detection:
            correct_count = sum(1 for r in lang_detection if r["is_correct"])
            total_count = len(lang_detection)
            accuracy_percent = (correct_count / total_count) * 100
            
            avg_confidence = statistics.mean(r["confidence"] for r in lang_detection)
            
            summary["language_detection"] = {
                "accuracy_percent": accuracy_percent,
                "correct_detections": correct_count,
                "total_detections": total_count,
                "avg_confidence": avg_confidence
            }
        
        # Semantic consistency
        semantic_consistency = self.accuracy_metrics["semantic_consistency"]
        if semantic_consistency:
            consistent_count = sum(1 for r in semantic_consistency if r["is_consistent"])
            total_count = len(semantic_consistency)
            consistency_percent = (consistent_count / total_count) * 100
            
            avg_overlap = statistics.mean(r["overlap_score"] for r in semantic_consistency)
            
            summary["semantic_consistency"] = {
                "consistency_percent": consistency_percent,
                "consistent_results": consistent_count,
                "total_comparisons": total_count,
                "avg_overlap_score": avg_overlap
            }
        
        return summary