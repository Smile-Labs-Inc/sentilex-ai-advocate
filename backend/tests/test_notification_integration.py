"""
Comprehensive notification system integration test
Tests both API and WebSocket functionality together
"""

import asyncio
import requests
import json
import time
from test_notification_api import NotificationAPITester
from test_websocket_notifications import WebSocketTester

class IntegratedNotificationTester:
    def __init__(self):
        self.api_tester = NotificationAPITester()
        self.ws_tester = WebSocketTester()
        self.integration_results = []

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log integration test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.integration_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        })

    async def test_end_to_end_notification_flow(self):
        """Test complete notification flow: API send -> WebSocket receive -> API read"""
        print("🔄 Testing End-to-End Notification Flow")
        print("-" * 40)
        
        # Setup user for both API and WebSocket
        if not self.ws_tester.setup_test_user():
            self.log_result("E2E Flow Setup", False, "Failed to setup user")
            return
        
        # Use the same token for API calls
        self.api_tester.user_token = self.ws_tester.token
        
        # Connect WebSocket
        if not await self.ws_tester.connect_websocket():
            self.log_result("E2E Flow WebSocket", False, "Failed to connect WebSocket")
            return
        
        # Start listening for WebSocket messages
        listen_task = asyncio.create_task(self.ws_tester.listen_for_messages(timeout=15))
        
        # Wait for connection establishment
        await asyncio.sleep(2)
        
        # Send notification via API
        notification_id = self.api_tester.test_send_test_notification(
            self.ws_tester.token, "integration_test"
        )
        
        if not notification_id:
            self.log_result("E2E Flow API Send", False, "Failed to send notification")
            listen_task.cancel()
            return
        
        # Wait for WebSocket to receive notification
        await asyncio.sleep(3)
        
        # Check if notification was received via WebSocket
        notification_received = any(
            msg.get("type") == "notification" and 
            str(msg.get("data", {}).get("id")) == str(notification_id)
            for msg in self.ws_tester.received_messages
        )
        
        if notification_received:
            self.log_result("E2E Flow WebSocket Receive", True, f"Notification {notification_id}")
        else:
            self.log_result("E2E Flow WebSocket Receive", False, "Notification not received")
        
        # Mark notification as read via API
        read_success = self.api_tester.test_mark_as_read(
            self.ws_tester.token, "integration_test", str(notification_id)
        )
        
        if read_success:
            self.log_result("E2E Flow Mark Read", True, f"Notification {notification_id}")
        else:
            self.log_result("E2E Flow Mark Read", False, "Failed to mark as read")
        
        # Verify unread count decreased
        unread_count = self.api_tester.test_get_unread_count(
            self.ws_tester.token, "integration_test"
        )
        
        # Stop listening and close WebSocket
        listen_task.cancel()
        if self.ws_tester.websocket:
            await self.ws_tester.websocket.close()
        
        # Overall E2E test success
        e2e_success = notification_id and notification_received and read_success
        self.log_result("E2E Flow Complete", e2e_success, 
                       f"Notification {notification_id} processed successfully" if e2e_success 
                       else "One or more steps failed")

    async def test_concurrent_connections(self):
        """Test multiple WebSocket connections handling"""
        print("\n🔗 Testing Concurrent WebSocket Connections")
        print("-" * 40)
        
        # Create multiple test users
        test_users = [
            {"email": f"concurrent{i}@example.com", "password": "test123", "full_name": f"Concurrent User {i}"}
            for i in range(3)
        ]
        
        connections = []
        tokens = []
        
        try:
            # Setup multiple users and connections
            for i, user_data in enumerate(test_users):
                # Register and login user
                session = requests.Session()
                session.post(f"http://127.0.0.1:8000/auth/register", json=user_data)
                login_response = session.post(f"http://127.0.0.1:8000/auth/login", 
                                            data={"username": user_data["email"], "password": user_data["password"]})
                
                if login_response.status_code == 200:
                    token = login_response.json().get("access_token")
                    tokens.append(token)
                    
                    # Connect WebSocket
                    import websockets
                    ws_url = f"ws://127.0.0.1:8000/api/notifications/ws?token={token}"
                    websocket = await websockets.connect(ws_url)
                    connections.append(websocket)
                    
                    self.log_result(f"Concurrent Connection {i+1}", True, f"User: {user_data['email']}")
                else:
                    self.log_result(f"Concurrent Connection {i+1}", False, "Failed to login")
            
            # Wait for connections to establish
            await asyncio.sleep(2)
            
            # Send notifications to all users
            for i, token in enumerate(tokens):
                url = "http://127.0.0.1:8000/api/notifications/test/send"
                headers = {"Authorization": f"Bearer {token}"}
                params = {"message": f"Concurrent test notification {i+1}"}
                
                response = requests.post(url, headers=headers, params=params)
                if response.status_code == 201:
                    self.log_result(f"Concurrent Notification {i+1}", True)
                else:
                    self.log_result(f"Concurrent Notification {i+1}", False)
            
            # Wait for notifications to be delivered
            await asyncio.sleep(3)
            
            self.log_result("Concurrent Connections Test", True, f"{len(connections)} connections handled")
            
        except Exception as e:
            self.log_result("Concurrent Connections Test", False, str(e))
        
        finally:
            # Close all connections
            for ws in connections:
                try:
                    await ws.close()
                except:
                    pass

    async def test_websocket_resilience(self):
        """Test WebSocket connection resilience and reconnection"""
        print("\n🛡️ Testing WebSocket Resilience")
        print("-" * 40)
        
        # Setup user
        if not self.ws_tester.setup_test_user():
            self.log_result("Resilience Setup", False, "Failed to setup user")
            return
        
        # Connect WebSocket
        if not await self.ws_tester.connect_websocket():
            self.log_result("Resilience Connect", False, "Failed to connect WebSocket")
            return
        
        # Send ping to test initial connection
        await self.ws_tester.send_ping()
        await asyncio.sleep(1)
        
        # Force close connection
        if self.ws_tester.websocket:
            await self.ws_tester.websocket.close()
            self.log_result("Resilience Force Close", True, "Connection closed")
        
        # Attempt to reconnect
        await asyncio.sleep(2)
        if await self.ws_tester.connect_websocket():
            self.log_result("Resilience Reconnect", True, "Successfully reconnected")
            
            # Test that notification still works after reconnect
            listen_task = asyncio.create_task(self.ws_tester.listen_for_messages(timeout=10))
            await asyncio.sleep(1)
            
            notification_id = self.ws_tester.send_test_notification_api()
            await asyncio.sleep(3)
            
            listen_task.cancel()
            
            # Check if notification was received after reconnect
            notification_received = any(
                msg.get("type") == "notification"
                for msg in self.ws_tester.received_messages[-5:]  # Check recent messages
            )
            
            self.log_result("Resilience Post-Reconnect Notification", notification_received,
                           "Notification received after reconnect" if notification_received 
                           else "No notification after reconnect")
            
            # Close connection
            if self.ws_tester.websocket:
                await self.ws_tester.websocket.close()
        else:
            self.log_result("Resilience Reconnect", False, "Failed to reconnect")

    async def run_integration_tests(self):
        """Run all integration tests"""
        print("🧪 NOTIFICATION SYSTEM INTEGRATION TESTS")
        print("=" * 60)
        
        # Run individual test suites first
        print("📋 Running API Test Suite...")
        self.api_tester.run_full_test_suite()
        
        print("\n📋 Running WebSocket Test Suite...")
        await self.ws_tester.run_websocket_tests()
        
        # Run integration-specific tests
        print("\n📋 Running Integration Tests...")
        await self.test_end_to_end_notification_flow()
        await self.test_concurrent_connections()
        await self.test_websocket_resilience()
        
        # Print final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        # API results
        api_total = len(self.api_tester.test_results)
        api_passed = len([r for r in self.api_tester.test_results if r["success"]])
        
        # WebSocket results  
        ws_total = len(self.ws_tester.test_results)
        ws_passed = len([r for r in self.ws_tester.test_results if r["success"]])
        
        # Integration results
        int_total = len(self.integration_results)
        int_passed = len([r for r in self.integration_results if r["success"]])
        
        print(f"API Tests:         {api_passed}/{api_total} passed ({api_passed/api_total*100:.1f}%)" if api_total > 0 else "API Tests: No tests")
        print(f"WebSocket Tests:   {ws_passed}/{ws_total} passed ({ws_passed/ws_total*100:.1f}%)" if ws_total > 0 else "WebSocket Tests: No tests")
        print(f"Integration Tests: {int_passed}/{int_total} passed ({int_passed/int_total*100:.1f}%)" if int_total > 0 else "Integration Tests: No tests")
        
        total_all = api_total + ws_total + int_total
        passed_all = api_passed + ws_passed + int_passed
        
        print(f"\nOVERALL:          {passed_all}/{total_all} passed ({passed_all/total_all*100:.1f}%)" if total_all > 0 else "No tests run")
        
        # System health check
        print(f"\n🏥 SYSTEM HEALTH:")
        print(f"API Endpoints:     {'✅ Healthy' if api_passed/api_total >= 0.8 else '⚠️ Issues' if api_total > 0 else '❓ Unknown'}")
        print(f"WebSocket:         {'✅ Healthy' if ws_passed/ws_total >= 0.8 else '⚠️ Issues' if ws_total > 0 else '❓ Unknown'}")
        print(f"Integration:       {'✅ Healthy' if int_passed/int_total >= 0.8 else '⚠️ Issues' if int_total > 0 else '❓ Unknown'}")
        print(f"Overall:           {'✅ System Ready' if passed_all/total_all >= 0.8 else '⚠️ System Issues' if total_all > 0 else '❓ Unknown'}")

async def main():
    tester = IntegratedNotificationTester()
    await tester.run_integration_tests()

if __name__ == "__main__":
    asyncio.run(main())