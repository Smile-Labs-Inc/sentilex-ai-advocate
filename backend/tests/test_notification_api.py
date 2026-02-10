"""
Test script for Notification API endpoints
Tests all notification router endpoints to ensure they're working correctly
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER = {
    "email": "testuser@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}
TEST_LAWYER = {
    "email": "testlawyer@example.com", 
    "password": "testpassword123",
    "full_name": "Test Lawyer"
}
TEST_ADMIN = {
    "email": "testadmin@example.com",
    "password": "testpassword123", 
    "full_name": "Test Admin"
}

class NotificationAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.lawyer_token = None
        self.admin_token = None
        self.test_results = []

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

    def register_and_login_user(self, user_data: Dict[str, str], user_type: str = "user") -> Optional[str]:
        """Register and login a user, return JWT token"""
        try:
            # Register user
            register_url = f"{BASE_URL}/auth/register"
            if user_type == "lawyer":
                register_url = f"{BASE_URL}/auth/lawyers/register"
            elif user_type == "admin":
                register_url = f"{BASE_URL}/auth/admin/register"

            register_response = self.session.post(register_url, json=user_data)
            
            # Login user
            login_url = f"{BASE_URL}/auth/login"
            if user_type == "lawyer":
                login_url = f"{BASE_URL}/auth/lawyers/login"
            elif user_type == "admin":
                login_url = f"{BASE_URL}/auth/admin/login"

            login_data = {
                "username": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = self.session.post(login_url, data=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                return token_data.get("access_token")
            else:
                self.log_result(f"Login {user_type}", False, f"Status: {login_response.status_code}")
                return None
                
        except Exception as e:
            self.log_result(f"Register/Login {user_type}", False, str(e))
            return None

    def setup_test_users(self):
        """Setup test users for notification testing"""
        print("🔧 Setting up test users...")
        
        self.user_token = self.register_and_login_user(TEST_USER, "user")
        if self.user_token:
            self.log_result("Setup User", True)
        else:
            self.log_result("Setup User", False, "Failed to get user token")

        self.lawyer_token = self.register_and_login_user(TEST_LAWYER, "lawyer") 
        if self.lawyer_token:
            self.log_result("Setup Lawyer", True)
        else:
            self.log_result("Setup Lawyer", False, "Failed to get lawyer token")

        self.admin_token = self.register_and_login_user(TEST_ADMIN, "admin")
        if self.admin_token:
            self.log_result("Setup Admin", True) 
        else:
            self.log_result("Setup Admin", False, "Failed to get admin token")

    def test_send_test_notification(self, token: str, user_type: str):
        """Test sending a test notification"""
        try:
            url = f"{BASE_URL}/api/notifications/test/send"
            headers = {"Authorization": f"Bearer {token}"}
            params = {"message": f"Test notification for {user_type}"}
            
            response = self.session.post(url, headers=headers, params=params)
            
            if response.status_code == 201:
                data = response.json()
                notification_id = data.get("id")
                self.log_result(f"Send Test Notification ({user_type})", True, f"ID: {notification_id}")
                return notification_id
            else:
                self.log_result(f"Send Test Notification ({user_type})", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result(f"Send Test Notification ({user_type})", False, str(e))
            return None

    def test_get_notifications(self, token: str, user_type: str):
        """Test getting notifications for user"""
        try:
            url = f"{BASE_URL}/api/notifications/my"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                count = len(notifications)
                self.log_result(f"Get Notifications ({user_type})", True, f"Found {count} notifications")
                return notifications
            else:
                self.log_result(f"Get Notifications ({user_type})", False, f"Status: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_result(f"Get Notifications ({user_type})", False, str(e))
            return []

    def test_get_unread_count(self, token: str, user_type: str):
        """Test getting unread notification count"""
        try:
            url = f"{BASE_URL}/api/notifications/my/unread-count"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                unread_count = data.get("unread_count", 0)
                self.log_result(f"Get Unread Count ({user_type})", True, f"Count: {unread_count}")
                return unread_count
            else:
                self.log_result(f"Get Unread Count ({user_type})", False, f"Status: {response.status_code}")
                return 0
                
        except Exception as e:
            self.log_result(f"Get Unread Count ({user_type})", False, str(e))
            return 0

    def test_mark_as_read(self, token: str, user_type: str, notification_id: str):
        """Test marking notification as read"""
        try:
            url = f"{BASE_URL}/api/notifications/my/mark-read"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            data = {"notification_ids": [notification_id]}
            
            response = self.session.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                self.log_result(f"Mark As Read ({user_type})", success, f"Notification: {notification_id}")
                return success
            else:
                self.log_result(f"Mark As Read ({user_type})", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(f"Mark As Read ({user_type})", False, str(e))
            return False

    def test_mark_all_read(self, token: str, user_type: str):
        """Test marking all notifications as read"""
        try:
            url = f"{BASE_URL}/api/notifications/my/mark-all-read"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = self.session.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                self.log_result(f"Mark All Read ({user_type})", success)
                return success
            else:
                self.log_result(f"Mark All Read ({user_type})", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(f"Mark All Read ({user_type})", False, str(e))
            return False

    def test_admin_send_notification(self):
        """Test admin sending notification to user"""
        if not self.admin_token:
            self.log_result("Admin Send Notification", False, "No admin token")
            return

        try:
            url = f"{BASE_URL}/api/notifications/send"
            headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
            data = {
                "recipient_id": 1,  # Assuming user ID 1
                "recipient_type": "USER",
                "title": "Admin Test Notification",
                "message": "This is a test notification from admin",
                "notification_type": "SYSTEM",
                "priority": 2
            }
            
            response = self.session.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                notification_id = result.get("id")
                self.log_result("Admin Send Notification", True, f"ID: {notification_id}")
                return notification_id
            else:
                self.log_result("Admin Send Notification", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Admin Send Notification", False, str(e))
            return None

    def test_unauthorized_access(self):
        """Test accessing endpoints without authentication"""
        endpoints = [
            "/api/notifications/my",
            "/api/notifications/my/unread-count",
            "/api/notifications/test/send"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                response = self.session.get(url)
                
                # Should return 401 or 422 for unauthorized access
                if response.status_code in [401, 422]:
                    self.log_result(f"Unauthorized Access {endpoint}", True, "Properly rejected")
                else:
                    self.log_result(f"Unauthorized Access {endpoint}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Unauthorized Access {endpoint}", False, str(e))

    def run_full_test_suite(self):
        """Run the complete notification API test suite"""
        print("🧪 Starting Notification API Test Suite")
        print("=" * 50)
        
        # Setup
        self.setup_test_users()
        print()
        
        # Test unauthorized access
        print("🔒 Testing unauthorized access...")
        self.test_unauthorized_access()
        print()
        
        # Test each user type
        user_types = [
            ("user", self.user_token),
            ("lawyer", self.lawyer_token), 
            ("admin", self.admin_token)
        ]
        
        for user_type, token in user_types:
            if not token:
                continue
                
            print(f"👤 Testing {user_type} endpoints...")
            
            # Send test notification
            notification_id = self.test_send_test_notification(token, user_type)
            
            # Get notifications
            notifications = self.test_get_notifications(token, user_type)
            
            # Get unread count
            unread_count = self.test_get_unread_count(token, user_type)
            
            # Mark as read (if we have a notification)
            if notification_id:
                self.test_mark_as_read(token, user_type, str(notification_id))
            
            # Mark all as read
            self.test_mark_all_read(token, user_type)
            
            print()
        
        # Test admin-specific endpoints
        if self.admin_token:
            print("👑 Testing admin-specific endpoints...")
            self.test_admin_send_notification()
            print()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

if __name__ == "__main__":
    tester = NotificationAPITester()
    tester.run_full_test_suite()