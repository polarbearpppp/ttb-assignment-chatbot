import requests
import json
import os
import time

# Update this to your FastAPI endpoint
BASE_URL = "http://localhost:8000/chat"

def run_tests():
    # Load cases from your file
    with open('test_case.json', 'r') as f:
        test_cases = json.load(f)

    print(f"{'='*50}")
    print(f"🚀 TTB CHATBOT API TEST SUITE")
    print(f"{'='*50}\n")

    for case in test_cases:
        print(f"▶️ Scenario: {case['name']}")
        print(f"💬 User: {case['payload']['message']}")
        
        try:
            # Prepare payload with correct field names
            payload = {
                "user_input": case['payload']['message'],
                "thread_id": case['payload']['thread_id']
            }
            
            # Send to FastAPI
            response = requests.post(BASE_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result.get('response', 'No response')}")
                print(f"📌 Decision: {result.get('decision', 'N/A')}")
                print(f"📊 Metadata: {result.get('metadata', {})}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"💀 Connection Error: {e}")
            
        print("-" * 30)
        time.sleep(1) # Slight delay to mimic human speed

if __name__ == "__main__":
    run_tests()