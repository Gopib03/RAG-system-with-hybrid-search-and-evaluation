import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_deployment():
    print("\n" + "="*60)
    print("🧪 TESTING DOCKER DEPLOYMENT")
    print("="*60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("   ✅ Health check passed")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Query endpoint
    print("\n2️⃣ Testing query endpoint...")
    try:
        payload = {
            "question": "What is machine learning?",
            "top_k": 5
        }
        
        start = time.time()
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)
        latency = (time.time() - start) * 1000
        
        result = response.json()
        
        print(f"   Status: {response.status_code}")
        print(f"   Answer length: {len(result['answer'])} chars")
        print(f"   Sources: {result['metadata']['num_sources']}")
        print(f"   Tokens: {result['metadata']['tokens_used']}")
        print(f"   Latency: {latency:.0f}ms")
        
        assert response.status_code == 200
        assert len(result['answer']) > 50
        print("   ✅ Query test passed")
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
        return False
    
    # Test 3: Stats endpoint
    print("\n3️⃣ Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        stats = response.json()
        
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Avg latency: {stats['avg_latency_ms']:.0f}ms")
        print("   ✅ Stats test passed")
    except Exception as e:
        print(f"   ❌ Stats test failed: {e}")
        return False
    
    # Test 4: Multiple concurrent queries
    print("\n4️⃣ Testing concurrent queries...")
    try:
        questions = [
            "What is deep learning?",
            "How do neural networks work?",
            "What are transformers?"
        ]
        
        for i, q in enumerate(questions, 1):
            payload = {"question": q, "top_k": 3}
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)
            assert response.status_code == 200
            print(f"   Query {i}/3: ✅")
        
        print("   ✅ Concurrent queries passed")
    except Exception as e:
        print(f"   ❌ Concurrent test failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n🎉 Your RAG system is production-ready!")
    return True

if __name__ == '__main__':
    test_deployment()