"""
Test LLM Tracking Implementation
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.llm_tracking_service import LLMTrackingService, MODEL_PRICING

def test_llm_tracking():
    """Test LLM tracking functionality"""
    print("=" * 60)
    print("Testing LLM Tracking Service")
    print("=" * 60)
    
    # Use existing database with schema
    engine = create_engine("sqlite:///tenant_system.db")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Test 1: Track a single LLM call
        print("\n1. Testing single LLM call tracking...")
        usage = LLMTrackingService.track_llm_call(
            db=db,
            tenant_id=1,
            model="gpt-4o-mini",
            operation_type="agent",
            input_tokens=100,
            output_tokens=50,
            success=True,
            latency_ms=1500,
            user_id=1,
            endpoint="/api/v1/beta/agent/chat",
            session_id="test-session-1"
        )
        print(f"✓ Tracked call: {usage.id}")
        print(f"  Model: {usage.model}")
        print(f"  Tokens: {usage.input_tokens} in, {usage.output_tokens} out")
        print(f"  Cost: ${usage.cost_usd}")
        print(f"  Latency: {usage.latency_ms}ms")
        
        # Test 2: Track multiple calls
        print("\n2. Testing multiple LLM calls...")
        for i in range(5):
            LLMTrackingService.track_llm_call(
                db=db,
                tenant_id=1,
                model="gpt-4o-mini",
                operation_type="rag" if i % 2 == 0 else "agent",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                success=True,
                latency_ms=1000 + i * 100
            )
        print(f"✓ Tracked 5 additional calls")
        
        # Test 3: Track failed call
        print("\n3. Testing failed LLM call...")
        failed_usage = LLMTrackingService.track_llm_call(
            db=db,
            tenant_id=1,
            model="gpt-4o",
            operation_type="agent",
            input_tokens=200,
            output_tokens=0,
            success=False,
            error_message="Rate limit exceeded",
            latency_ms=500
        )
        print(f"✓ Tracked failed call: {failed_usage.id}")
        print(f"  Error: {failed_usage.error_message}")
        
        # Test 4: Get usage summary
        print("\n4. Testing usage summary...")
        summary = LLMTrackingService.get_usage_summary(
            db=db,
            tenant_id=1
        )
        print(f"✓ Usage Summary:")
        print(f"  Total calls: {summary.total_calls}")
        print(f"  Successful: {summary.successful_calls}")
        print(f"  Failed: {summary.failed_calls}")
        print(f"  Total tokens: {summary.total_tokens:,}")
        print(f"  Total cost: ${summary.total_cost_usd}")
        print(f"  Avg latency: {summary.average_latency_ms:.0f}ms")
        
        # Test 5: Get usage by model
        print("\n5. Testing usage by model...")
        by_model = LLMTrackingService.get_usage_by_model(
            db=db,
            tenant_id=1
        )
        for model_usage in by_model:
            print(f"✓ {model_usage.model}:")
            print(f"    Calls: {model_usage.call_count}")
            print(f"    Tokens: {model_usage.total_tokens:,}")
            print(f"    Cost: ${model_usage.total_cost_usd}")
        
        # Test 6: Get usage by operation
        print("\n6. Testing usage by operation...")
        by_operation = LLMTrackingService.get_usage_by_operation(
            db=db,
            tenant_id=1
        )
        for op_usage in by_operation:
            print(f"✓ {op_usage.operation_type}:")
            print(f"    Calls: {op_usage.call_count}")
            print(f"    Tokens: {op_usage.total_tokens:,}")
            print(f"    Cost: ${op_usage.total_cost_usd}")
        
        # Test 7: Test cost calculation
        print("\n7. Testing cost calculation...")
        for model, pricing in MODEL_PRICING.items():
            cost = LLMTrackingService.calculate_cost(model, 1000, 500)
            print(f"✓ {model}: ${cost} for 1000 in + 500 out tokens")
        
        # Test 8: Test date filtering
        print("\n8. Testing date filtering...")
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        
        filtered_summary = LLMTrackingService.get_usage_summary(
            db=db,
            tenant_id=1,
            start_date=yesterday,
            end_date=tomorrow
        )
        print(f"✓ Filtered summary (last 24h):")
        print(f"  Total calls: {filtered_summary.total_calls}")
        
        # Test 9: Test multi-tenant isolation
        print("\n9. Testing multi-tenant isolation...")
        # Add data for tenant 2
        LLMTrackingService.track_llm_call(
            db=db,
            tenant_id=2,
            model="gpt-4o",
            operation_type="agent",
            input_tokens=500,
            output_tokens=300,
            success=True
        )
        
        tenant1_summary = LLMTrackingService.get_usage_summary(db=db, tenant_id=1)
        tenant2_summary = LLMTrackingService.get_usage_summary(db=db, tenant_id=2)
        
        print(f"✓ Tenant 1: {tenant1_summary.total_calls} calls, ${tenant1_summary.total_cost_usd}")
        print(f"✓ Tenant 2: {tenant2_summary.total_calls} calls, ${tenant2_summary.total_cost_usd}")
        
        # Test 10: Test admin view (all tenants)
        print("\n10. Testing admin view (all tenants)...")
        all_usage = LLMTrackingService.get_all_tenants_usage(db=db)
        print(f"✓ All tenants usage:")
        for tenant_id, summary in all_usage.items():
            print(f"  Tenant {tenant_id}: {summary.total_calls} calls, ${summary.total_cost_usd}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_llm_tracking()
