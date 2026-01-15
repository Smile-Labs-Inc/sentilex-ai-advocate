"""
Setup Script for SentiLex AI Advocate Backend

This script helps set up the development environment.
Run with: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        sys.exit(1)

    print("✅ Python version is compatible")


def check_env_file():
    """Check if .env file exists."""
    print_header("Checking Environment Configuration")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found")
            print("📋 Copying .env.example to .env...")

            with open(env_example, "r") as src:
                content = src.read()

            with open(env_file, "w") as dst:
                dst.write(content)

            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file exists")

    # Check for required keys
    with open(env_file, "r") as f:
        content = f.read()

    if "your_openai_api_key_here" in content:
        print("⚠️  WARNING: OPENAI_API_KEY not configured in .env")
        print("   Please edit .env and add your OpenAI API key")

    return True


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")

    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    print("📦 Installing packages from requirements.txt...")
    print("   This may take a few minutes...\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")

    directories = [
        "logs",
        "data",
    ]

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✓  Directory exists: {directory}")


def verify_structure():
    """Verify project structure."""
    print_header("Verifying Project Structure")

    required_files = [
        "app.py",
        "requirements.txt",
        "agents/__init__.py",
        "chains/__init__.py",
        "schemas/__init__.py",
        "mcp_client/__init__.py",
        "logging/__init__.py",
    ]

    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False

    return all_good


def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete!")

    print("""
Next Steps:

1. Configure your OpenAI API key:
   - Open .env file
   - Replace 'your_openai_api_key_here' with your actual key
   - Get a key from: https://platform.openai.com/api-keys

2. (Optional) Configure MCP service:
   - Set MCP_HOST and MCP_PORT in .env if not using localhost:3000
   - Ensure MCP service is running

3. Run the system:
   - Start server: python app.py
   - Run tests: python test_system.py
   - API docs: http://localhost:8000/docs

4. Read the documentation:
   - Architecture: ARCHITECTURE.md
   - README: README.md
   - System diagram: SYSTEM_DIAGRAM.md

For help, visit: http://localhost:8000/docs
    """)


def main():
    """Run setup process."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   SentiLex AI Advocate - Backend Setup                   ║
║   Multi-Agent Legal Reasoning System                      ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Run all checks and setup steps
    check_python_version()

    if not check_env_file():
        print("\n❌ Setup failed: Environment configuration error")
        sys.exit(1)

    if not install_dependencies():
        print("\n❌ Setup failed: Dependency installation error")
        sys.exit(1)

    create_directories()

    if not verify_structure():
        print("\n⚠️  Warning: Some files are missing")
        print("   The system may not work correctly")

    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {str(e)}")
        sys.exit(1)
