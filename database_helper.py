import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import uuid
import hashlib
import json

class Database:
    def __init__(self):
        self.url = st.secrets.get('SUPABASE_URL', '')
        self.key = st.secrets.get('SUPABASE_KEY', '')
        if self.url and self.key:
            self.client = create_client(self.url, self.key)
        else:
            self.client = None
    
    def verify_user(self, username, password):
        if not self.client:
            return None
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = self.client.table('users').select('*').eq('username', username).eq('password_hash', password_hash).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_user_by_id(self, user_id):
        if not self.client:
            return None
        result = self.client.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    
    def get_all_users(self):
        if not self.client:
            return []
        result = self.client.table('users').select('*').execute()
        return result.data
    
    def create_workflow(self, title, description, platform, initiator_id, approver_ids, expires_days=30):
        if not self.client:
            return None
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        workflow = {
            'id': workflow_id,
            'title': title,
            'description': description,
            'platform': platform,
            'status': 'pending',
            'initiator_id': initiator_id,
            'document_path': None,
            'priority': 'Medium',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expires_days)).isoformat(),
            'completed_at': None
        }
        self.client.table('workflows').insert(workflow).execute()
        
        for i, approver_id in enumerate(approver_ids):
            approver = {
                'id': f"APR-{uuid.uuid4().hex[:8].upper()}",
                'workflow_id': workflow_id,
                'user_id': approver_id,
                'order_number': i + 1,
                'status': 'pending',
                'signed_at': None,
                'comments': ''
            }
            self.client.table('approvers').insert(approver).execute()
        
        return workflow_id
    
    def create_workflow_with_doc(self, title, description, platform, initiator_id, approver_ids, document_path, expires_days=30):
        workflow_id = self.create_workflow(title, description, platform, initiator_id, approver_ids, expires_days)
        if workflow_id and self.client:
            self.client.table('workflows').update({'document_path': document_path}).eq('id', workflow_id).execute()
        return workflow_id
    
    def get_workflows_by_user(self, user_id, role):
        if not self.client:
            return []
        
        if role == 'admin':
            result = self.client.table('workflows').select('*').order('created_at', desc=True).execute()
        else:
            result = self.client.table('workflows').select('*').or_(f'initiator_id.eq.{user_id}').order('created_at', desc=True).execute()
        
        workflows = result.data
        
        for wf in workflows:
            approvers_result = self.client.table('approvers').select('*, users!inner(full_name, email)').eq('workflow_id', wf['id']).execute()
            wf['approvers'] = []
            for a in approvers_result.data:
                approver_data = {
                    'id': a['id'],
                    'workflow_id': a['workflow_id'],
                    'user_id': a['user_id'],
                    'status': a['status'],
                    'signed_at': a['signed_at'],
                    'comments': a.get('comments', ''),
                    'full_name': a.get('users', {}).get('full_name', ''),
                    'email': a.get('users', {}).get('email', '')
                }
                wf['approvers'].append(approver_data)
            
            initiator = self.get_user_by_id(wf['initiator_id'])
            wf['initiator_name'] = initiator['full_name'] if initiator else ''
        
        return workflows
    
    def sign_workflow(self, workflow_id, approver_id, comments=''):
        if not self.client:
            return
        self.client.table('approvers').update({
            'status': 'signed',
            'signed_at': datetime.now().isoformat(),
            'comments': comments
        }).eq('workflow_id', workflow_id).eq('user_id', approver_id).execute()
        
        # Check if all signed
        approvers = self.client.table('approvers').select('*').eq('workflow_id', workflow_id).execute()
        if all(a['status'] == 'signed' for a in approvers.data):
            self.client.table('workflows').update({
                'status': 'approved',
                'completed_at': datetime.now().isoformat()
            }).eq('id', workflow_id).execute()
    
    def update_workflow_status(self, workflow_id, status, user_id):
        if not self.client:
            return
        self.client.table('workflows').update({'status': status}).eq('id', workflow_id).execute()
    
    def add_notification(self, user_id, message, notification_type):
        pass
    
    def get_notifications(self, user_id, limit=10):
        return []
    
    def get_workflow_stats(self):
        if not self.client:
            return {'total': 0, 'status_counts': {}, 'platform_counts': {}, 'avg_approval_time': 0}
        
        workflows = self.client.table('workflows').select('*').execute().data
        
        status_counts = {}
        platform_counts = {}
        for wf in workflows:
            status_counts[wf['status']] = status_counts.get(wf['status'], 0) + 1
            platform_counts[wf['platform']] = platform_counts.get(wf['platform'], 0) + 1
        
        return {
            'total': len(workflows),
            'status_counts': status_counts,
            'platform_counts': platform_counts,
            'avg_approval_time': 0
        }
    
    def get_audit_trail(self, limit=50):
        if not self.client:
            return []
        result = self.client.table('audit_trail').select('*, users(full_name)').order('timestamp', desc=True).limit(limit).execute()
        entries = []
        for row in result.data:
            entries.append({
                'timestamp': row.get('timestamp', ''),
                'full_name': row.get('users', {}).get('full_name', ''),
                'action': row.get('action', ''),
                'details': row.get('details', ''),
                'workflow_title': row.get('workflow_id', ''),
                'workflow_id': row.get('workflow_id', '')
            })
        return entries
    
    def save_platform_config(self, platform_name, config):
        if not self.client:
            return
        existing = self.client.table('platform_configs').select('*').eq('platform_name', platform_name).execute()
        data = {
            'platform_name': platform_name,
            'api_key': json.dumps(config),
            'is_connected': True,
            'settings': json.dumps(config),
            'last_sync': datetime.now().isoformat()
        }
        if existing.data:
            self.client.table('platform_configs').update(data).eq('platform_name', platform_name).execute()
        else:
            data['id'] = f"PLT-{uuid.uuid4().hex[:8].upper()}"
            self.client.table('platform_configs').insert(data).execute()
    
    def get_platform_config(self, platform_name):
        if not self.client:
            return None
        result = self.client.table('platform_configs').select('*').eq('platform_name', platform_name).eq('is_connected', True).execute()
        if result.data and result.data[0].get('settings'):
            return json.loads(result.data[0]['settings'])
        return None
    
    def conn(self):
        return self