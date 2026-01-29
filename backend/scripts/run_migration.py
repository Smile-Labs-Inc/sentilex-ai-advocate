#!/usr/bin/env python
"""
Database Migration Helper Script

This script helps manage Alembic migrations for the SentiLex AI Advocate system.

Usage:
    python run_migration.py upgrade    # Apply all pending migrations
    python run_migration.py downgrade  # Rollback one migration
    python run_migration.py current    # Show current revision
    python run_migration.py history    # Show migration history
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command


def get_alembic_config():
    """Get Alembic configuration"""
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    return config


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    action = sys.argv[1].lower()
    config = get_alembic_config()
    
    try:
        if action == "upgrade":
            # Apply all pending migrations
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            print(f"📦 Upgrading database to: {revision}")
            command.upgrade(config, revision)
            print("✅ Migration completed successfully!")
            
        elif action == "downgrade":
            # Rollback migrations
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            print(f"⏪ Downgrading database to: {revision}")
            command.downgrade(config, revision)
            print("✅ Rollback completed successfully!")
            
        elif action == "current":
            # Show current revision
            print("📍 Current database revision:")
            command.current(config)
            
        elif action == "history":
            # Show migration history
            print("📜 Migration history:")
            command.history(config)
            
        elif action == "stamp":
            # Mark database as being at specific revision (without running migrations)
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            print(f"🏷️  Stamping database at revision: {revision}")
            command.stamp(config, revision)
            print("✅ Database stamped successfully!")
            
        elif action == "generate":
            # Auto-generate a new migration
            message = sys.argv[2] if len(sys.argv) > 2 else "auto_generated"
            print(f"🔨 Generating new migration: {message}")
            command.revision(config, message=message, autogenerate=True)
            print("✅ Migration generated successfully!")
            
        else:
            print(f"❌ Unknown action: {action}")
            print(__doc__)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
