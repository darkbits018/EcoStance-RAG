#!/usr/bin/env python3
"""
Migration runner script for Better RBAC Phase 1.
Helps execute the database schema and data migrations.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config.database import get_database_url


def run_sql_migration():
    """Run the SQL schema migration."""
    print("=== Running SQL Schema Migration ===")
    
    migration_file = Path(__file__).parent.parent / "migrations" / "001_better_rbac_phase1.sql"
    
    if not migration_file.exists():
        print(f"Migration file not found: {migration_file}")
        return False
    
    database_url = get_database_url()
    
    # Extract connection details from database URL
    # Format: postgresql://user:password@host:port/database
    if not database_url.startswith("postgresql://"):
        print("Only PostgreSQL databases are supported for this migration")
        return False
    
    print(f"Migration file: {migration_file}")
    print("Please run the following command manually with psql:")
    print(f"psql '{database_url}' -f '{migration_file}'")
    print()
    print("Or connect to your database and execute the SQL commands from the migration file.")
    print()
    
    return True


def run_data_migration():
    """Run the data migration script."""
    print("=== Running Data Migration ===")
    
    data_migration_script = Path(__file__).parent / "migrate_rbac_data.py"
    
    if not data_migration_script.exists():
        print(f"Data migration script not found: {data_migration_script}")
        return False
    
    try:
        # Run the data migration script
        result = subprocess.run([
            sys.executable, str(data_migration_script)
        ], capture_output=True, text=True)
        
        print("Data migration output:")
        print(result.stdout)
        
        if result.stderr:
            print("Data migration errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("Data migration completed successfully!")
            return True
        else:
            print(f"Data migration failed with exit code: {result.returncode}")
            return False
    
    except Exception as e:
        print(f"Error running data migration: {e}")
        return False


def main():
    """Main migration runner."""
    print("Better RBAC Phase 1 Migration Runner")
    print("====================================")
    print()
    
    print("This migration will:")
    print("1. Add the tenant_roles table")
    print("2. Add system_role and tenant_role_id columns to tenant_users")
    print("3. Create default tenant roles for existing tenants")
    print("4. Migrate existing user roles to the new system")
    print()
    
    # Step 1: SQL Migration
    if not run_sql_migration():
        print("SQL migration setup failed. Please run the SQL migration manually.")
        return
    
    print("After running the SQL migration, press Enter to continue with data migration...")
    input()
    
    # Step 2: Data Migration
    if not run_data_migration():
        print("Data migration failed. Please check the errors above.")
        return
    
    print()
    print("=== Migration Complete ===")
    print("Phase 1 of Better RBAC has been implemented!")
    print()
    print("Next steps:")
    print("1. Test the new RBAC system")
    print("2. Update your application code to use the new role system")
    print("3. Consider implementing Phase 2 (API endpoints)")
    print("4. Eventually remove the legacy 'role' column after full migration")


if __name__ == "__main__":
    main()