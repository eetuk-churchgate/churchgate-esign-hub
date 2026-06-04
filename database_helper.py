import sqlite3
from datetime import datetime, timedelta
import uuid
import hashlib
import streamlit as st

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('esign_hub.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    # User operations
    def verify_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1', 
                      (username, password_hash))
        user = cursor.fetchone()
        if user:
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            self.conn.commit()
            return dict(user)
        return None
    
    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE is_active = 1')
        return [dict(row) for row in cursor.fetchall()]
    
    # Workflow operations
    def create_workflow(self, title, description, platform, initiator_id, approver_ids, expires_days=30):
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO workflows (id, title, description, platform, status, initiator_id, expires_at)
            VALUES (?, ?, ?, ?, 'pending', ?, ?)
        ''', (workflow_id, title, description, platform, initiator_id, 
              (datetime.now() + timedelta(days=expires_days)).isoformat()))
        
        # Add approvers
        for i, approver_id in enumerate(approver_ids):
            approver_record_id = f"APR-{uuid.uuid4().hex[:8].upper()}"
            cursor.execute('''
                INSERT INTO approvers (id, workflow_id, user_id, order_number, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (approver_record_id, workflow_id, approver_id, i + 1))
        
        # Add audit entry
        self.add_audit_entry(workflow_id, initiator_id, 'created', f'Workflow created with {len(approver_ids)} approvers')
        
        self.conn.commit()
        return workflow_id
    
    def get_workflows_by_user(self, user_id, role):
        cursor = self.conn.cursor()
        if role == 'admin':
            cursor.execute('''
                SELECT w.*, u.full_name as initiator_name 
                FROM workflows w 
                JOIN users u ON w.initiator_id = u.id 
                ORDER BY w.created_at DESC
            ''')
        else:
            # User can see workflows they initiated or need to approve
            cursor.execute('''
                SELECT DISTINCT w.*, u.full_name as initiator_name 
                FROM workflows w 
                JOIN users u ON w.initiator_id = u.id 
                LEFT JOIN approvers a ON w.id = a.workflow_id 
                WHERE w.initiator_id = ? OR a.user_id = ?
                ORDER BY w.created_at DESC
            ''', (user_id, user_id))
        
        workflows = []
        for row in cursor.fetchall():
            workflow = dict(row)
            # Get approvers for this workflow
            cursor.execute('''
                SELECT a.*, u.full_name, u.email 
                FROM approvers a 
                JOIN users u ON a.user_id = u.id 
                WHERE a.workflow_id = ?
                ORDER BY a.order_number
            ''', (workflow['id'],))
            workflow['approvers'] = [dict(a) for a in cursor.fetchall()]
            workflows.append(workflow)
        
        return workflows
    
    def update_workflow_status(self, workflow_id, status, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE workflows SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                      (status, workflow_id))
        if status == 'approved':
            cursor.execute('UPDATE workflows SET completed_at = CURRENT_TIMESTAMP WHERE id = ?', (workflow_id,))
        self.add_audit_entry(workflow_id, user_id, f'status_changed', f'Status changed to {status}')
        self.conn.commit()
    
    def sign_workflow(self, workflow_id, approver_id, comments=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE approvers 
            SET status = 'signed', signed_at = CURRENT_TIMESTAMP, comments = ?
            WHERE workflow_id = ? AND user_id = ? AND status = 'pending'
        ''', (comments, workflow_id, approver_id))
        
        # Check if all approvers have signed
        cursor.execute('''
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status = 'signed' THEN 1 ELSE 0 END) as signed_count
            FROM approvers 
            WHERE workflow_id = ?
        ''', (workflow_id,))
        result = cursor.fetchone()
        
        if result['total'] == result['signed_count']:
            self.update_workflow_status(workflow_id, 'approved', approver_id)
        
        self.add_audit_entry(workflow_id, approver_id, 'signed', f'Document signed with comments: {comments}')
        self.conn.commit()
    
    # Audit operations
    def add_audit_entry(self, workflow_id, user_id, action, details):
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO audit_trail (id, workflow_id, user_id, action, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (audit_id, workflow_id, user_id, action, details))
        self.conn.commit()
    
    def get_audit_trail(self, workflow_id=None, limit=50):
        cursor = self.conn.cursor()
        if workflow_id:
            cursor.execute('''
                SELECT a.*, u.full_name 
                FROM audit_trail a 
                JOIN users u ON a.user_id = u.id 
                WHERE a.workflow_id = ? 
                ORDER BY a.timestamp DESC 
                LIMIT ?
            ''', (workflow_id, limit))
        else:
            cursor.execute('''
                SELECT a.*, u.full_name, w.title as workflow_title
                FROM audit_trail a 
                JOIN users u ON a.user_id = u.id 
                JOIN workflows w ON a.workflow_id = w.id 
                ORDER BY a.timestamp DESC 
                LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Notification operations
    def add_notification(self, user_id, message, notification_type):
        notif_id = f"NOT-{uuid.uuid4().hex[:8].upper()}"
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (id, user_id, message, type)
            VALUES (?, ?, ?, ?)
        ''', (notif_id, user_id, message, notification_type))
        self.conn.commit()
    
    def get_notifications(self, user_id, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_workflow_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT status, COUNT(*) as count FROM workflows GROUP BY status')
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT platform, COUNT(*) as count FROM workflows GROUP BY platform')
        platform_counts = {row['platform']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT COUNT(*) as total FROM workflows')
        total = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT AVG(julianday(completed_at) - julianday(created_at)) as avg_days 
            FROM workflows 
            WHERE completed_at IS NOT NULL
        ''')
        avg_time = cursor.fetchone()['avg_days'] or 0
        
        return {
            'total': total,
            'status_counts': status_counts,
            'platform_counts': platform_counts,
            'avg_approval_time': round(avg_time, 1)
        }
