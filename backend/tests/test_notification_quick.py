#!/usr/bin/env python3
"""
Quick notification system test runner
Runs basic tests to verify the notification system is working
"""

import requests
import json
import time
import sys
import asyncio
import websockets
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def create_test_user() -> Optional[str]:
    """Create test user and return JWT token"""
    user_data = {
        "email": f"quicktest{int(time.time())}@example.com",
        "password": "testpass123",
        "full_name": "Quick Test User"
    }
    
    try:
        # Register
        register_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        # Login
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("✅ Test user created and authenticated")
            return token
        else:
            print(f"❌ Failed to authenticate test user: {login_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return None

def test_notification_api(token: str) -> Optional[str]:
    """Test notification API endpoints"""
    try:
        # Send test notification
        headers = {"Authorization": f"Bearer {token}"}
        params = {"message": "Quick test notification"}
        
        response = requests.post(f"{BASE_URL}/api/notifications/test/send", 
                               headers=headers, params=params)
        
        if response.status_code == 201:
            notification_id = str(response.json().get("id"))
            print(f"✅ Notification API working (ID: {notification_id})")
            return notification_id
        else:
            print(f"❌ Notification API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Notification API error: {e}")
        return None

async def test_websocket(token: str) -> bool:
    """Test WebSocket connection and message receiving"""
    try:
        # Connect to WebSocket
        ws_url = f"{WS_URL}/api/notifications/ws?token={token}"
        websocket = await websockets.connect(ws_url)
        print("✅ WebSocket connected")
        
        # Listen for connection established message
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            parsed = json.loads(message)
            
            if parsed.get("type") == "connection_established":
                print("✅ WebSocket connection established")
                await websocket.close()
                return True
            else:
                print(f"⚠️ Unexpected first message: {parsed.get('type')}")
                await websocket.close()
                return False
                
        except asyncio.TimeoutError:
            print("❌ WebSocket connection timeout")
            await websocket.close()
            return False
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_websocket_notification(token: str) -> bool:
    """Test WebSocket notification delivery"""
    try:
        # Connect WebSocket
        ws_url = f"{WS_URL}/api/notifications/ws?token={token}"
        websocket = await websockets.connect(ws_url)
        
        # Wait for connection established
        await asyncio.wait_for(websocket.recv(), timeout=5.0)
        
        # Send notification via API
        headers = {"Authorization": f"Bearer {token}"}
        params = {"message": "WebSocket delivery test"}
        
        response = requests.post(f"{BASE_URL}/api/notifications/test/send", 
                               headers=headers, params=params)
        
        if response.status_code != 201:
            print(f"❌ Failed to send test notification: {response.status_code}")
            await websocket.close()
            return False
        
        notification_id = str(response.json().get("id"))
        
        # Wait for WebSocket notification
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            parsed = json.loads(message)
            
            if (parsed.get("type") == "notification" and 
                str(parsed.get("data", {}).get("id")) == notification_id):
                print("✅ WebSocket notification delivery working")
                await websocket.close()
                return True
            else:
                print(f"⚠️ Received unexpected message: {parsed.get('type')}")
                await websocket.close()
                return False
                
        except asyncio.TimeoutError:
            print("❌ WebSocket notification not received (timeout)")
            await websocket.close()
            return False
            
    except Exception as e:
        print(f"❌ WebSocket notification test failed: {e}")
        return False

async def main():
    """Run quick notification system tests"""
    print("🧪 Quick Notification System Test")
    print("=" * 40)
    
    # Test backend
    if not test_backend_health():
        print("\n❌ Backend not available. Start the backend with:")
        print("   cd backend && uvicorn main:app --reload")
        sys.exit(1)
    
    # Create test user
    token = create_test_user()
    if not token:
        sys.exit(1)
    
    # Test API
    notification_id = test_notification_api(token)
    if not notification_id:
        sys.exit(1)
    
    # Test WebSocket connection
    ws_connected = await test_websocket(token)
    if not ws_connected:
        print("⚠️ WebSocket connection issues")
    
    # Test WebSocket notification delivery
    ws_notification = await test_websocket_notification(token)
    if not ws_notification:
        print("⚠️ WebSocket notification delivery issues")
    
    # Summary
    print("\n📊 Quick Test Summary")
    print("-" * 25)
    print(f"Backend Health:    ✅")
    print(f"User Auth:         ✅")
    print(f"Notification API:  ✅")
    print(f"WebSocket Connect: {'✅' if ws_connected else '❌'}")
    print(f"WebSocket Notify:  {'✅' if ws_notification else '❌'}")
    
    if ws_connected and ws_notification:
        print("\n🎉 Notification system is working!")
        print("\nNext steps:")
        print("1. Add the NotificationTest component to your frontend")
        print("2. Test browser notifications")
        print("3. Run full test suite: python tests/test_notification_integration.py")
    else:
        print(f"\n⚠️ Some issues detected. Check the logs above.")
        if not ws_connected:
            print("- WebSocket connection failed")
        if not ws_notification:
            print("- WebSocket notifications not working")

if __name__ == "__main__":
    asyncio.run(main())