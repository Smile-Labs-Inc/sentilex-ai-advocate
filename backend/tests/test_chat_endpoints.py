"""
Test Chat Endpoints
Tests all chat-related API endpoints including:
- POST /api/chat/send (auto-save chat)
- GET /api/chat/history (get past chats)
- GET /api/chat/sessions/{id} (get full conversation)
- DELETE /api/chat/sessions/{id} (delete chat)
"""

import requests
import time
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8001"

# Test user credentials
TEST_EMAIL = "sarah.smith@example.com"
TEST_PASSWORD = "MyPassword2024@"
TEST_FIRST_NAME = "Sarah"
TEST_LAST_NAME = "Smith"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")

def print_error(message: str):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")

def print_section(message: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def register_test_user() -> Optional[str]:
    """Register a test user and return access token"""
    print_info(f"Registering test user: {TEST_EMAIL}")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "first_name": TEST_FIRST_NAME,
            "last_name": TEST_LAST_NAME,
            "district": "Gampaha",
            "preferred_language": "en"
        }
    )
    
    if response.status_code == 201:
        print_success("User registered successfully")
        return response.json().get("access_token")
    elif response.status_code == 400 and "already registered" in response.text.lower():
        print_info("User already exists, attempting login...")
        return login_test_user()
    else:
        print_error(f"Registration failed: {response.status_code} - {response.text}")
        return None

def login_test_user() -> Optional[str]:
    """Login test user and return access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        print_success("User logged in successfully")
        return response.json().get("access_token")
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_send_chat_message(token: str, message: str, session_id: Optional[str] = None) -> Optional[dict]:
    """Test POST /api/chat/send endpoint"""
    print_info(f"Sending message: '{message[:50]}...'")
    
    payload = {
        "message": message,
        "metadata": {"test": True}
    }
    
    if session_id:
        payload["session_id"] = session_id
        print_info(f"Using existing session: {session_id}")
    else:
        print_info("Creating new session")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/send",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Message sent successfully!")
        print(f"  Session ID: {data['session_id']}")
        print(f"  Session Title: {data['session']['title']}")
        print(f"  User Message ID: {data['user_message']['id']}")
        print(f"  Assistant Message ID: {data['assistant_message']['id']}")
        print(f"  Assistant Response: {data['assistant_message']['content'][:100]}...")
        return data
    else:
        print_error(f"Send message failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_get_chat_history(token: str, limit: int = 50) -> Optional[list]:
    """Test GET /api/chat/history endpoint"""
    print_info(f"Getting chat history (limit: {limit})")
    
    response = requests.get(
        f"{BASE_URL}/api/chat/history",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": limit}
    )
    
    if response.status_code == 200:
        sessions = response.json()
        print_success(f"Retrieved {len(sessions)} chat sessions")
        for i, session in enumerate(sessions[:5], 1):  # Show first 5
            print(f"  {i}. {session['title']} - {session['message_count']} messages")
            print(f"     Last message: {session.get('last_message', 'N/A')[:50]}...")
        return sessions
    else:
        print_error(f"Get history failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_get_session_with_messages(token: str, session_id: str) -> Optional[dict]:
    """Test GET /api/chat/sessions/{id} endpoint"""
    print_info(f"Getting session details: {session_id}")
    
    response = requests.get(
        f"{BASE_URL}/api/chat/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 100}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        print_success(f"Retrieved session: {session_data['title']}")
        print(f"  Message count: {len(session_data['messages'])}")
        print(f"  Messages:")
        for i, msg in enumerate(session_data['messages'][:6], 1):  # Show first 6
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            print(f"    {i}. {role_icon} {msg['role']}: {msg['content'][:60]}...")
        return session_data
    else:
        print_error(f"Get session failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_delete_session(token: str, session_id: str) -> bool:
    """Test DELETE /api/chat/sessions/{id} endpoint"""
    print_info(f"Deleting session: {session_id}")
    
    response = requests.delete(
        f"{BASE_URL}/api/chat/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 204:
        print_success("Session deleted successfully")
        return True
    else:
        print_error(f"Delete session failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return False

def test_get_chat_stats(token: str) -> Optional[dict]:
    """Test GET /api/chat/stats endpoint"""
    print_info("Getting chat statistics")
    
    response = requests.get(
        f"{BASE_URL}/api/chat/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_success(f"Chat stats retrieved")
        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  User ID: {stats['user_id']}")
        return stats
    else:
        print_error(f"Get stats failed: {response.status_code}")
        return None

def test_create_and_update_session(token: str) -> Optional[str]:
    """Test POST /api/chat/sessions endpoint"""
    print_info("Creating new session manually")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Manual Test Session"}
    )
    
    if response.status_code == 201:
        session = response.json()
        print_success(f"Session created: {session['id']}")
        print(f"  Title: {session['title']}")
        return session['id']
    else:
        print_error(f"Create session failed: {response.status_code}")
        return None

def test_update_session_title(token: str, session_id: str, new_title: str) -> bool:
    """Test PATCH /api/chat/sessions/{id} endpoint"""
    print_info(f"Updating session title to: '{new_title}'")
    
    response = requests.patch(
        f"{BASE_URL}/api/chat/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": new_title}
    )
    
    if response.status_code == 200:
        session = response.json()
        print_success(f"Session title updated: {session['title']}")
        return True
    else:
        print_error(f"Update session failed: {response.status_code}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of all chat endpoints"""
    print_section("CHAT ENDPOINTS COMPREHENSIVE TEST")
    
    # Step 1: Setup - Login with existing user
    print_section("Step 1: Authentication Setup")
    token = login_test_user()
    if not token:
        print_error("Failed to authenticate. Cannot proceed with tests.")
        return False
    
    test_passed = 0
    test_failed = 0
    
    # Step 2: Test creating new chat (auto-session creation)
    print_section("Step 2: Send First Message (Auto-Create Session)")
    chat_data = test_send_chat_message(token, "What are my rights in a cybercrime case?")
    if chat_data:
        test_passed += 1
        session_id = chat_data['session_id']
    else:
        test_failed += 1
        print_error("Cannot proceed without session ID")
        return False
    
    time.sleep(0.5)
    
    # Step 3: Send another message to same session
    print_section("Step 3: Send Second Message (Same Session)")
    chat_data2 = test_send_chat_message(
        token, 
        "How do I collect digital evidence?",
        session_id=session_id
    )
    if chat_data2:
        test_passed += 1
        # Verify it's the same session
        if chat_data2['session_id'] == session_id:
            print_success("✓ Message added to existing session correctly")
        else:
            print_error("✗ Message created new session instead of using existing")
            test_failed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 4: Get chat history
    print_section("Step 4: Get Chat History (Sidebar)")
    sessions = test_get_chat_history(token, limit=20)
    if sessions:
        test_passed += 1
        if len(sessions) > 0:
            print_success(f"✓ Found {len(sessions)} session(s) in history")
        else:
            print_error("✗ No sessions found in history")
            test_failed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 5: Get full conversation
    print_section("Step 5: Get Full Conversation")
    session_details = test_get_session_with_messages(token, session_id)
    if session_details:
        test_passed += 1
        if len(session_details['messages']) >= 4:  # 2 user + 2 assistant
            print_success(f"✓ Retrieved all {len(session_details['messages'])} messages")
        else:
            print_error(f"✗ Expected at least 4 messages, got {len(session_details['messages'])}")
            test_failed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 6: Get chat stats
    print_section("Step 6: Get Chat Statistics")
    stats = test_get_chat_stats(token)
    if stats:
        test_passed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 7: Create another session for testing
    print_section("Step 7: Create New Chat Session")
    chat_data3 = test_send_chat_message(token, "Tell me about the Computer Crimes Act")
    if chat_data3:
        test_passed += 1
        session_id_2 = chat_data3['session_id']
    else:
        test_failed += 1
        session_id_2 = None
    
    time.sleep(0.5)
    
    # Step 8: Update session title
    if session_id_2:
        print_section("Step 8: Update Session Title")
        if test_update_session_title(token, session_id_2, "Computer Crimes Act Discussion"):
            test_passed += 1
        else:
            test_failed += 1
    
    time.sleep(0.5)
    
    # Step 9: Verify history shows both sessions
    print_section("Step 9: Verify Multiple Sessions in History")
    sessions_after = test_get_chat_history(token)
    if sessions_after:
        test_passed += 1
        if len(sessions_after) >= 2:
            print_success(f"✓ Found {len(sessions_after)} sessions (expected >= 2)")
        else:
            print_error(f"✗ Expected at least 2 sessions, found {len(sessions_after)}")
            test_failed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 10: Delete one session
    print_section("Step 10: Delete Chat Session")
    if session_id_2 and test_delete_session(token, session_id_2):
        test_passed += 1
    else:
        test_failed += 1
    
    time.sleep(0.5)
    
    # Step 11: Verify deletion
    print_section("Step 11: Verify Session Deleted")
    sessions_final = test_get_chat_history(token)
    if sessions_final:
        test_passed += 1
        # Check that session_id_2 is not in the list
        if session_id_2:
            session_ids = [s['id'] for s in sessions_final]
            if session_id_2 not in session_ids:
                print_success("✓ Deleted session no longer appears in history")
            else:
                print_error("✗ Deleted session still appears in history")
                test_failed += 1
    else:
        test_failed += 1
    
    # Final Summary
    print_section("TEST SUMMARY")
    total_tests = test_passed + test_failed
    success_rate = (test_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  {Colors.GREEN}Passed: {test_passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {test_failed}{Colors.RESET}")
    print(f"  {Colors.CYAN}Success Rate: {success_rate:.1f}%{Colors.RESET}")
    
    if test_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Chat system is working perfectly!{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Some tests failed. Please review the errors above.{Colors.RESET}\n")
        return False

def test_edge_cases(token: str):
    """Test edge cases and error handling"""
    print_section("EDGE CASES & ERROR HANDLING")
    
    # Test 1: Empty message
    print_info("Test: Empty message")
    response = requests.post(
        f"{BASE_URL}/api/chat/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": ""}
    )
    if response.status_code == 422:  # Validation error expected
        print_success("✓ Empty message correctly rejected")
    else:
        print_error(f"✗ Unexpected response: {response.status_code}")
    
    # Test 2: Invalid session ID
    print_info("Test: Invalid session ID")
    response = requests.post(
        f"{BASE_URL}/api/chat/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Test",
            "session_id": "00000000-0000-0000-0000-000000000000"
        }
    )
    if response.status_code == 404:  # Session not found
        print_success("✓ Invalid session ID correctly handled")
    else:
        print_error(f"✗ Unexpected response: {response.status_code}")
    
    # Test 3: Get non-existent session
    print_info("Test: Get non-existent session")
    response = requests.get(
        f"{BASE_URL}/api/chat/sessions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 404:
        print_success("✓ Non-existent session correctly handled")
    else:
        print_error(f"✗ Unexpected response: {response.status_code}")
    
    # Test 4: Delete non-existent session
    print_info("Test: Delete non-existent session")
    response = requests.delete(
        f"{BASE_URL}/api/chat/sessions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 404:
        print_success("✓ Delete non-existent session correctly handled")
    else:
        print_error(f"✗ Unexpected response: {response.status_code}")
    
    # Test 5: Very long message
    print_info("Test: Very long message (10,000 chars)")
    long_message = "A" * 10000
    response = requests.post(
        f"{BASE_URL}/api/chat/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": long_message}
    )
    if response.status_code == 200:
        print_success("✓ Long message handled correctly")
    else:
        print_error(f"✗ Long message failed: {response.status_code}")

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        CHAT ENDPOINTS COMPREHENSIVE TEST SUITE            ║")
    print("║                                                            ║")
    print("║  Testing all chat-related API endpoints:                  ║")
    print("║  • POST   /api/chat/send                                  ║")
    print("║  • GET    /api/chat/history                               ║")
    print("║  • GET    /api/chat/sessions/{id}                         ║")
    print("║  • PATCH  /api/chat/sessions/{id}                         ║")
    print("║  • DELETE /api/chat/sessions/{id}                         ║")
    print("║  • GET    /api/chat/stats                                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    try:
        # Run main test suite
        success = run_comprehensive_test()
        
        # Run edge case tests
        print("\n")
        token = login_test_user()
        if token:
            test_edge_cases(token)
        
        # Exit with appropriate code
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        exit(1)
