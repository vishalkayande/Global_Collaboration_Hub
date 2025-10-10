#!/usr/bin/env python3
"""
Database migration script to add new columns to existing tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add new columns to existing database tables"""
    
    # Database path
    db_path = os.path.join('instance', 'data.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database...")
        return
    
    print("Migrating database...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if memberships table exists and get its columns
        cursor.execute("PRAGMA table_info(memberships)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current memberships columns: {columns}")
        
        # Add new columns if they don't exist
        if 'status' not in columns:
            print("Adding status column to memberships table...")
            cursor.execute("ALTER TABLE memberships ADD COLUMN status VARCHAR(20) DEFAULT 'invited'")
        
        if 'invited_by' not in columns:
            print("Adding invited_by column to memberships table...")
            cursor.execute("ALTER TABLE memberships ADD COLUMN invited_by INTEGER")
        
        if 'invited_at' not in columns:
            print("Adding invited_at column to memberships table...")
            cursor.execute("ALTER TABLE memberships ADD COLUMN invited_at DATETIME")
        
        if 'joined_at' not in columns:
            print("Adding joined_at column to memberships table...")
            cursor.execute("ALTER TABLE memberships ADD COLUMN joined_at DATETIME")
        
        # Check if password_resets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password_resets'")
        if not cursor.fetchone():
            print("Creating password_resets table...")
            cursor.execute("""
                CREATE TABLE password_resets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        
        # Update existing memberships to have 'accepted' status
        print("Updating existing memberships to 'accepted' status...")
        cursor.execute("UPDATE memberships SET status = 'accepted' WHERE status IS NULL")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

