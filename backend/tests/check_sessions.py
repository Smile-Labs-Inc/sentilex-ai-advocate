"""Check active sessions in database"""
from database.config import get_db
from models.active_session import ActiveSession
from models.user import User

db = next(get_db())

# Get user
user = db.query(User).filter(User.email == "dilani.w@yahoo.com").first()
if not user:
    print("❌ User not found")
else:
    print(f"✅ User found: ID={user.id}, Name={user.first_name} {user.last_name}")
    
    # Get sessions
    sessions = db.query(ActiveSession).filter(
        ActiveSession.user_id == user.id,
        ActiveSession.user_type == "user"
    ).all()
    
    print(f"\n📋 Active sessions for user {user.id}:")
    if not sessions:
        print("   No active sessions found")
    else:
        for s in sessions:
            print(f"   Session ID: {s.id}")
            print(f"   JTI: {s.jti}")
            print(f"   User Type: {s.user_type}")
            print(f"   Created: {s.created_at}")
            print(f"   Expires: {s.expires_at}")
            print()
