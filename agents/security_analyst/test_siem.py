"""
Test Script for Security Analyst SIEM Connection
"""
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.security_analyst.tools.siem_tools import search_siem_logs, get_log_volume_stats

# Configure logging to see the output
logging.basicConfig(level=logging.INFO)

def test_connection():
    print("--- Testing SIEM Login and Log Search ---")
    try:
        # 1. Test basic log search
        print("\nSearching for 'error' in syslog_logs-*...")
        search_result = search_siem_logs.invoke({
            "query_text": "error",
            "size": 5
        })
        print("Search Result (first 500 chars):")
        print(search_result[:500] + "...")
        
        # 2. Test log volume stats
        print("\nFetching log volume stats for the last 60 mins...")
        stats_result = get_log_volume_stats.invoke({
            "time_period_minutes": 60
        })
        print("Stats Result:")
        print(stats_result)
        
        print("\n--- Test Complete ---")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")

if __name__ == "__main__":
    test_connection()
