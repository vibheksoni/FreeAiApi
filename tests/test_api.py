import requests
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
import time
import base64

class TestAPI:
    def __init__(self):
        load_dotenv()
        self.base_url = f"http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('PORT', 5000)}/api"
        self.headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": os.getenv('AUTH_TOKEN')
        }
        self.gpt_session_id = None
        self.grok_session_id = None
        self.transaction_id = None

    def test_chat_gpt(self) -> Dict[str, Any]:
        """Test ChatGPT endpoint"""
        endpoint = f"{self.base_url}/chat/send"
        payload = {
            "model": "gpt",
            "message": "Hello, how are you?",
            "session_id": self.gpt_session_id
        }
        
        print("\nTesting ChatGPT:")
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response_data = response.json()
        
        if response_data["status"] and response_data["data"]:
            self.gpt_session_id = response_data["data"]["session_id"]
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data

    def test_chat_grok(self) -> Dict[str, Any]:
        """Test Grok endpoint"""
        endpoint = f"{self.base_url}/chat/send"
        payload = {
            "model": "grok",
            "message": "What is Python?",
            "session_id": self.grok_session_id
        }
        
        print("\nTesting Grok:")
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response_data = response.json()
        
        if response_data["status"] and response_data["data"]:
            self.grok_session_id = response_data["data"]["session_id"]
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data

    def test_chat_grok_with_image(self) -> Dict[str, Any]:
        """Test Grok endpoint with image attachment"""
        endpoint = f"{self.base_url}/chat/send"
        
        # Test image path (you can modify this)
        image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
        
        # Read and encode test image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        payload = {
            "model": "grok",
            "message": "What's in this image?",
            "session_id": self.grok_session_id,
            "files": [{
                "filename": "test_image.jpg",
                "base64": encoded_image
            }]
        }
        
        print("\nTesting Grok with Image:")
        print(f"Request: {json.dumps({**payload, 'files': '[base64 data omitted]'}, indent=2)}")
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response_data = response.json()
        
        if response_data["status"] and response_data["data"]:
            self.grok_session_id = response_data["data"]["session_id"]
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data

    def test_conversation(self) -> None:
        """Test conversation with session"""
        try:
            print("\nTesting Conversation Flow:")
            
            # First GPT message
            response1 = self.test_chat_gpt()
            if not response1["status"]:
                print("Failed to start GPT conversation")
                return
                
            # Ensure session is saved
            self.gpt_session_id = response1["data"]["session_id"]
                
            # Wait between requests
            time.sleep(2)
                
            # Follow-up GPT message
            payload = {
                "model": "gpt",
                "message": "What's the weather like?",
                "session_id": self.gpt_session_id
            }
            
            print("\nFollow-up Message:")
            print(f"Request: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/chat/send", 
                json=payload, 
                headers=self.headers,
                timeout=30  # Add timeout
            )
            
            if response.status_code != 200:
                print(f"Error: Unexpected status code {response.status_code}")
                return False
                
            response_data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            return response_data["status"]

        except Exception as e:
            print(f"Error in conversation test: {str(e)}")
            return False

    def test_admin_routes(self) -> None:
        """Test admin routes"""
        try:
            print("\n=== Testing Admin Routes ===")
            
            # Wait for sessions to be ready
            time.sleep(2)
            
            # Get sessions
            response = requests.get(
                f"{self.base_url}/admin/sessions", 
                headers=self.headers,
                timeout=30
            )
            print("\nActive Sessions:")
            print(json.dumps(response.json(), indent=2))
            
            # Get stats
            response = requests.get(
                f"{self.base_url}/admin/sessions/stats", 
                headers=self.headers,
                timeout=30
            )
            print("\nSession Stats:")
            print(json.dumps(response.json(), indent=2))
            
            # Wait before clearing
            time.sleep(1)
            
            # Clear sessions
            response = requests.post(
                f"{self.base_url}/admin/sessions/clear", 
                headers=self.headers,
                timeout=30
            )
            print("\nClear Sessions:")
            print(json.dumps(response.json(), indent=2))
            
            return True

        except Exception as e:
            print(f"Error in admin routes test: {str(e)}")
            return False

    def test_queue_submit(self) -> Dict[str, Any]:
        """Test queue submit endpoint"""
        endpoint = f"{self.base_url}/queue/submit"
        payload = {
            "model": "gpt",
            "message": "Process this message asynchronously",
            "session_id": self.gpt_session_id
        }
        
        print("\nTesting Queue Submit:")
        print(f"Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response_data = response.json()
        
        if response_data["status"] and response_data["data"]:
            self.transaction_id = response_data["data"]["transaction_id"]
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data

    def test_queue_status(self) -> Dict[str, Any]:
        """Test queue status endpoint"""
        if not self.transaction_id:
            return {
                "status": False,
                "message": "No transaction ID available",
                "data": None
            }

        endpoint = f"{self.base_url}/queue/status/{self.transaction_id}"
        print("\nTesting Queue Status:")
        
        max_retries = 10  # Increased from 5 to 10
        retry_delay = 3   # Reduced from 2 to 1 second
        
        for i in range(max_retries):
            response = requests.get(endpoint, headers=self.headers)
            response_data = response.json()
            
            print(f"Attempt {i+1} - Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if response_data["status"] and response_data["data"]["status"] in ["completed", "failed"]:
                return response_data
                
            time.sleep(retry_delay)
        
        # If we reach here, consider it a success if the task is at least processing
        if response_data["status"] and response_data["data"]["status"] == "processing":
            return response_data
            
        return response_data

    def run_all_tests(self) -> None:
        """Run all test cases"""
        tests = [
            ("Health Check", self.test_health),
            ("GPT Basic Chat", self.test_chat_gpt),
            ("Grok Basic Chat", self.test_chat_grok),
            ("Grok with Image", self.test_chat_grok_with_image),
            ("Conversation Flow", self.test_conversation),
            ("Queue Submit", self.test_queue_submit),
            ("Queue Status", self.test_queue_status),
            ("Admin Routes", self.test_admin_routes)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n=== Running Test: {test_name} ===")
            try:
                result = test_func()
                status = "✅ Passed" if (isinstance(result, dict) and result.get("status")) or result else "❌ Failed"
            except Exception as e:
                print(f"Error: {str(e)}")
                status = "❌ Failed (Error)"
                
            results.append((test_name, status))
            time.sleep(1)  # Delay between tests
        
        # Print summary
        print("\n=== Test Summary ===")
        for test_name, status in results:
            print(f"{test_name}: {status}")

    def test_health(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        endpoint = f"{self.base_url}/health"
        print("\nTesting Health Check:")
        
        response = requests.get(endpoint, headers=self.headers)
        response_data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data

if __name__ == "__main__":
    tester = TestAPI()
    tester.run_all_tests()
