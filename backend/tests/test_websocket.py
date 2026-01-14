#!/usr/bin/env python3
"""
Simple test script to verify WebSocket implementation
This tests the WebSocket endpoint and LangChain streaming service
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.langchain_websocket import langchain_websocket_service
from app.models.schemas import ScenarioConfig


async def test_langchain_streaming():
    """Test LangChain streaming service"""
    print("Testing LangChain Streaming Service...")
    print("-" * 50)
    
    # Create a simple scenario
    scenario = ScenarioConfig(
        context="Job interview for software engineer",
        target_audience="Senior hiring manager",
        purpose="Interview practice",
        target_language="English",
        custom_prompt=""
    )
    
    user_input = "Tell me about yourself"
    
    print(f"User input: {user_input}")
    print("\nAI Response (streaming):")
    print("-" * 50)
    
    full_response = ""
    chunk_count = 0
    
    try:
        async for chunk in langchain_websocket_service.stream_response(
            user_input, scenario, []
        ):
            print(chunk, end='', flush=True)
            full_response += chunk
            chunk_count += 1
        
        print("\n" + "-" * 50)
        print(f"\nTotal chunks received: {chunk_count}")
        print(f"Full response length: {len(full_response)} characters")
        print("\n✅ LangChain streaming test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ LangChain streaming test FAILED: {str(e)}")
        return False


async def test_complete_response():
    """Test non-streaming response"""
    print("\n\nTesting Complete Response (non-streaming)...")
    print("-" * 50)
    
    scenario = ScenarioConfig(
        context="Customer service call",
        target_audience="Frustrated customer",
        purpose="Customer service practice",
        target_language="English",
        custom_prompt="Be empathetic and solution-focused"
    )
    
    user_input = "I'm having issues with my order"
    
    print(f"User input: {user_input}")
    print("\nAI Response:")
    print("-" * 50)
    
    try:
        response = await langchain_websocket_service.generate_complete_response(
            user_input, scenario, []
        )
        
        print(response)
        print("-" * 50)
        print(f"Response length: {len(response)} characters")
        print("\n✅ Complete response test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Complete response test FAILED: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("=" * 50)
    print("WebSocket Implementation Tests")
    print("=" * 50)
    print("\nNote: These tests require valid Azure OpenAI credentials")
    print("in the .env file or environment variables.\n")
    
    results = []
    
    # Test 1: Streaming
    results.append(await test_langchain_streaming())
    
    # Test 2: Complete response
    results.append(await test_complete_response())
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
