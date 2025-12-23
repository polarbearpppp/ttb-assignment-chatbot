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
            # Send to FastAPI
            response = requests.post(BASE_URL, json=case['payload'])
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result['response']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"💀 Connection Error: {e}")
            
        print("-" * 30)
        time.sleep(1) # Slight delay to mimic human speed

if __name__ == "__main__":
    run_tests()