#!/usr/bin/env python3
"""Clean up duplicate records from irrigation_decisions database"""

import sqlite3

DB_PATH = 'Code/backend/data/irrigation_decisions.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete records with timestamp starting with 2026-03-05T23:28:53
    cursor.execute("""
        DELETE FROM irrigation_decisions 
        WHERE timestamp LIKE '2026-03-05T23:28:53%'
    """)
    
    deleted = cursor.rowcount
    conn.commit()
    
    # Show remaining records
    cursor.execute("SELECT COUNT(*) FROM irrigation_decisions")
    remaining = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✓ Deleted {deleted} record(s)")
    print(f"✓ Remaining records: {remaining}")
    
except Exception as e:
    print(f"✗ Error: {e}")
