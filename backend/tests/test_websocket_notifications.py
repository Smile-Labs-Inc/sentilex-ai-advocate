"""
Test script for WebSocket notification functionality
Tests real-time notification delivery via WebSocket
"""

import asyncio
import json
import time
import requests
import websockets
from typing import Optional, Dict, Any, List
import threading
import jwt
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"
TEST_USER = {
    "email": "wstest@example.com",
    "password": "testpassword123",
    "full_name": "WebSocket Test User"
}

class WebSocketTester:
    def __init__(self):
        self.token = None
        self.websocket = None
        self.received_messages = []
        self.test_results = []
        self.connection_established = False
        self.notification_received = False

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        })

    def setup_test_user(self) -> bool:
        """Setup test user and get JWT token"""
        try:
            session = requests.Session()
            
            # Register user
            register_response = session.post(f"{BASE_URL}/auth/register", json=TEST_USER)
            
            # Login user
            login_data = {
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.token = token_data.get("access_token")
                self.log_result("Setup Test User", True, "Token obtained")
                return True
            else:
                self.log_result("Setup Test User", False, f"Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Setup Test User", False, str(e))
            return False

    async def connect_websocket(self) -> bool:
        """Connect to WebSocket endpoint"""
        if not self.token:
            self.log_result("WebSocket Connect", False, "No token available")
            return False

        try:
            ws_url = f"{WS_URL}/api/notifications/ws?token={self.token}"
            self.websocket = await websockets.connect(ws_url)
            self.log_result("WebSocket Connect", True, "Connection established")
            return True
            
        except Exception as e:
            self.log_result("WebSocket Connect", False, str(e))
            return False

    async def listen_for_messages(self, timeout: int = 10):
        """Listen for WebSocket messages"""
        if not self.websocket:
            self.log_result("WebSocket Listen", False, "No WebSocket connection")
            return

        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Wait for message with short timeout
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    parsed_message = json.loads(message)
                    self.received_messages.append(parsed_message)
                    
                    print(f"📨 Received: {parsed_message.get('type', 'unknown')}")
                    
                    # Check message types
                    msg_type = parsed_message.get("type")
                    if msg_type == "connection_established":
                        self.connection_established = True
                        self.log_result("WebSocket Connection Established", True)
                    elif msg_type == "notification":
                        self.notification_received = True
                        notification_data = parsed_message.get("data", {})
                        self.log_result("WebSocket Notification Received", True, 
                                      f"ID: {notification_data.get('id')}")
                    elif msg_type == "pong":
                        self.log_result("WebSocket Pong Received", True)
                    
                except asyncio.TimeoutError:
                    # No message received in timeout period, continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    self.log_result("WebSocket Listen", False, "Connection closed")
                    break
                    
        except Exception as e:
            self.log_result("WebSocket Listen", False, str(e))

    async def send_ping(self) -> bool:
        """Send ping message to test connection"""
        if not self.websocket:
            self.log_result("WebSocket Ping", False, "No WebSocket connection")
            return False

        try:
            ping_message = json.dumps({"type": "ping"})
            await self.websocket.send(ping_message)
            self.log_result("WebSocket Ping Sent", True)
            return True
            
        except Exception as e:
            self.log_result("WebSocket Ping", False, str(e))
            return False

    async def send_mark_as_read(self, notification_id: str) -> bool:
        """Send mark as read message via WebSocket"""
        if not self.websocket:
            self.log_result("WebSocket Mark Read", False, "No WebSocket connection")
            return False

        try:
            mark_read_message = json.dumps({
                "type": "mark_as_read",
                "notification_id": notification_id
            })
            await self.websocket.send(mark_read_message)
            self.log_result("WebSocket Mark Read Sent", True, f"Notification: {notification_id}")
            return True
            
        except Exception as e:
            self.log_result("WebSocket Mark Read", False, str(e))
            return False

    def send_test_notification_api(self) -> Optional[str]:
        """Send test notification via API to trigger WebSocket notification"""
        if not self.token:
            self.log_result("API Test Notification", False, "No token available")
            return None

        try:
            url = f"{BASE_URL}/api/notifications/test/send"
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"message": "WebSocket test notification"}
            
            response = requests.post(url, headers=headers, params=params)
            
            if response.status_code == 201:
                data = response.json()
                notification_id = str(data.get("id"))
                self.log_result("API Test Notification Sent", True, f"ID: {notification_id}")
                return notification_id
            else:
                self.log_result("API Test Notification", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("API Test Notification", False, str(e))
            return None

    async def test_invalid_token(self):
        """Test WebSocket connection with invalid token"""
        try:
            invalid_token = "invalid.jwt.token"
            ws_url = f"{WS_URL}/api/notifications/ws?token={invalid_token}"
            
            try:
                websocket = await websockets.connect(ws_url)
                # If connection succeeds, wait for close
                await asyncio.sleep(2)
                self.log_result("Invalid Token Test", False, "Connection should have been rejected")
            except websockets.exceptions.ConnectionClosedError as e:
                # This is expected
                if e.code == 4001:  # Our custom close code for invalid token
                    self.log_result("Invalid Token Test", True, "Connection properly rejected")
                else:
                    self.log_result("Invalid Token Test", False, f"Unexpected close code: {e.code}")
            except Exception as e:
                self.log_result("Invalid Token Test", False, str(e))
                
        except Exception as e:
            self.log_result("Invalid Token Test", False, str(e))

    async def test_no_token(self):
        """Test WebSocket connection without token"""
        try:
            ws_url = f"{WS_URL}/api/notifications/ws"
            
            try:
                websocket = await websockets.connect(ws_url)
                await asyncio.sleep(2)
                self.log_result("No Token Test", False, "Connection should have been rejected")
            except Exception:
                # Connection should fail
                self.log_result("No Token Test", True, "Connection properly rejected")
                
        except Exception as e:
            self.log_result("No Token Test", False, str(e))

    async def run_websocket_tests(self):
        """Run comprehensive WebSocket tests"""
        print("🔌 Starting WebSocket Test Suite")
        print("=" * 50)
        
        # Setup user
        if not self.setup_test_user():
            print("❌ Failed to setup test user, aborting WebSocket tests")
            return
        
        print()
        
        # Test invalid scenarios first
        print("🚫 Testing invalid connection scenarios...")
        await self.test_invalid_token()
        await self.test_no_token()
        print()
        
        # Test valid connection
        print("✅ Testing valid WebSocket connection...")
        if not await self.connect_websocket():
            print("❌ Failed to connect to WebSocket, aborting tests")
            return
        
        # Start listening for messages in background
        listen_task = asyncio.create_task(self.listen_for_messages(timeout=30))
        
        # Give some time for connection establishment message
        await asyncio.sleep(2)
        
        # Test ping/pong
        print("\n🏓 Testing ping/pong...")
        await self.send_ping()
        await asyncio.sleep(1)
        
        # Send test notification via API
        print("\n📧 Testing notification delivery...")
        notification_id = self.send_test_notification_api()
        
        # Wait for WebSocket notification
        await asyncio.sleep(3)
        
        # Test mark as read via WebSocket
        if notification_id:
            print("\n✅ Testing mark as read via WebSocket...")
            await self.send_mark_as_read(notification_id)
            await asyncio.sleep(2)
        
        # Stop listening
        listen_task.cancel()
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.log_result("WebSocket Disconnect", True)
        
        print()
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("📊 WEBSOCKET TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        # Check key functionality
        print(f"\n🔍 Key Functionality:")
        print(f"Connection Established: {'✅' if self.connection_established else '❌'}")
        print(f"Notification Received: {'✅' if self.notification_received else '❌'}")
        print(f"Total Messages Received: {len(self.received_messages)}")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        if self.received_messages:
            print(f"\n📨 All Received Messages:")
            for i, msg in enumerate(self.received_messages, 1):
                print(f"  {i}. {msg.get('type', 'unknown')}: {json.dumps(msg, indent=2)}")

async def main():
    tester = WebSocketTester()
    await tester.run_websocket_tests()

if __name__ == "__main__":
    asyncio.run(main())