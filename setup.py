#!/usr/bin/env python3
"""Setup script for the player fouls prediction project."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✓ {description} completed")
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        sys.exit(1)


def main():
    """Set up the project environment."""
    print("Player Fouls Prediction Model - Setup")
    print("====================================")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        run_command(
            f"{sys.executable} -m venv venv",
            "Creating virtual environment"
        )
    else:
        print("✓ Virtual environment already exists")
    
    # Determine pip path
    pip_cmd = "venv/bin/pip" if sys.platform != "win32" else "venv\\Scripts\\pip"
    
    # Upgrade pip
    run_command(
        f"{pip_cmd} install --upgrade pip",
        "Upgrading pip"
    )
    
    # Install requirements
    run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Installing dependencies"
    )
    
    # Create .env file from example
    env_file = Path(".env")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from .env.example")
    
    # Initialize database
    print("\nInitializing database...")
    activate_cmd = "source venv/bin/activate" if sys.platform != "win32" else "venv\\Scripts\\activate"
    
    try:
        # Import and run database initialization
        sys.path.insert(0, str(Path(__file__).parent))
        from src.data.database import init_database
        init_database()
        print("✓ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("You can initialize it later by running:")
        print(f"  {activate_cmd} && python -c 'from src.data.database import init_database; init_database()'")
    
    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print(f"1. Activate virtual environment: {activate_cmd}")
    print("2. Test the setup: python scripts/collect_sample.py")
    print("\nYou'll need:")
    print("- A valid FBref match URL (e.g., https://fbref.com/en/matches/...)")
    print("- The exact player name as it appears on FBref")


if __name__ == "__main__":
    main()