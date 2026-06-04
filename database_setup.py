import sqlite3
from datetime import datetime, timedelta
import uuid
import hashlib

def init_database():
    conn = sqlite3.connect('esign_hub.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Workflows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            platform TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            initiator_id TEXT NOT NULL,
            document_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (initiator_id) REFERENCES users(id)
        )
    ''')
    
    # Approvers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approvers (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            order_number INTEGER,
            status TEXT DEFAULT 'pending',
            signed_at TIMESTAMP,
            comments TEXT,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Audit trail table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_trail (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Platform configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_configs (
            id TEXT PRIMARY KEY,
            platform_name TEXT NOT NULL,
            api_key TEXT,
            is_connected BOOLEAN DEFAULT 0,
            settings TEXT,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default users if not exist
    default_users = [
        ('USR-001', 'etuk', 'etuk@company.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Etuk Admin', 'IT', 'admin'),
        ('USR-002', 'lawal', 'lawal@company.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Lawal Manager', 'Legal', 'manager'),
        ('USR-003', 'john.doe', 'john@company.com', hashlib.sha256('password123'.encode()).hexdigest(), 'John Doe', 'Finance', 'user'),
        ('USR-004', 'jane.smith', 'jane@company.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Jane Smith', 'HR', 'user'),
    ]
    
    for user in default_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, department, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', user)
    
    # Insert platform configs
    platforms = [
        ('PLT-001', 'DocuSign', '', 0, '{}', None),
        ('PLT-002', 'HelloSign', '', 0, '{}', None),
        ('PLT-003', 'Microsoft 365', '', 0, '{}', None),
        ('PLT-004', 'Google Sign', '', 0, '{}', None),
    ]
    
    for platform in platforms:
        cursor.execute('''
            INSERT OR IGNORE INTO platform_configs (id, platform_name, api_key, is_connected, settings, last_sync)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', platform)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
