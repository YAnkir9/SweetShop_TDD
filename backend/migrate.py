#!/usr/bin/env python3
"""
Migration utility script for SweetShop TDD project.

This script provides convenient commands for common Alembic operations.
Usage: python migrate.py <command> [args]
"""

import sys
import subprocess
import os
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def show_help():
    """Display help information."""
    print("""
🍬 SweetShop TDD Migration Utility

Commands:
  status     - Show current migration status
  history    - Show migration history  
  check      - Verify schema consistency
  generate   - Generate new migration (requires message)
  upgrade    - Apply all pending migrations
  downgrade  - Rollback last migration
  reset      - Reset to base (⚠️  DESTRUCTIVE)
  
Examples:
  python migrate.py status
  python migrate.py generate "add user preferences table"
  python migrate.py upgrade
  python migrate.py downgrade
  
⚠️  Always backup your database before running migrations in production!
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Change to backend directory if not already there
    if not os.path.exists("alembic"):
        backend_path = os.path.join(os.path.dirname(__file__), "backend")
        if os.path.exists(backend_path):
            os.chdir(backend_path)
        else:
            print("❌ Error: Could not find alembic directory")
            return
    
    if command == "status":
        run_command(["alembic", "current"], "Checking current migration status")
        
    elif command == "history":
        run_command(["alembic", "history", "--verbose"], "Showing migration history")
        
    elif command == "check":
        success = run_command(["alembic", "check"], "Verifying schema consistency")
        if success:
            print("✅ Database schema is in sync with models")
        
    elif command == "generate":
        if len(sys.argv) < 3:
            print("❌ Error: Migration message is required")
            print("Usage: python migrate.py generate \"your migration message\"")
            return
        message = " ".join(sys.argv[2:])
        run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            f"Generating migration: {message}"
        )
        
    elif command == "upgrade":
        success = run_command(["alembic", "upgrade", "head"], "Applying migrations")
        if success:
            print("✅ All migrations applied successfully")
            
    elif command == "downgrade":
        run_command(["alembic", "downgrade", "-1"], "Rolling back last migration")
        
    elif command == "reset":
        confirm = input("⚠️  This will reset ALL migrations. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            run_command(["alembic", "downgrade", "base"], "Resetting all migrations")
        else:
            print("❌ Operation cancelled")
            
    elif command == "help":
        show_help()
        
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
