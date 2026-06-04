from datetime import datetime, timedelta

def get_sample_workflows():
    return [
        {
            'id': 'WF-001',
            'title': 'Contract Review - Vendor Agreement',
            'platform': 'DocuSign',
            'status': 'Pending Approval',
            'approvers': 3,
            'signed': 2,
            'created': '2024-01-15',
            'expires': '2024-01-30',
            'priority': 'High',
            'progress': 66,
            'department': 'Legal'
        },
        {
            'id': 'WF-002',
            'title': 'Budget Approval Q4 2024',
            'platform': 'MS365',
            'status': 'Pending Approval',
            'approvers': 2,
            'signed': 1,
            'created': '2024-01-14',
            'expires': '2024-01-29',
            'priority': 'High',
            'progress': 50,
            'department': 'Finance'
        },
        {
            'id': 'WF-003',
            'title': 'HR Policy Update 2024',
            'platform': 'HelloSign',
            'status': 'Approved',
            'approvers': 4,
            'signed': 4,
            'created': '2024-01-10',
            'expires': '2024-01-25',
            'priority': 'Medium',
            'progress': 100,
            'department': 'HR'
        },
        {
            'id': 'WF-004',
            'title': 'Vendor Onboarding - TechCorp',
            'platform': 'DocuSign',
            'status': 'Draft',
            'approvers': 2,
            'signed': 0,
            'created': '2024-01-16',
            'expires': '2024-02-15',
            'priority': 'Low',
            'progress': 0,
            'department': 'Operations'
        }
    ]

def get_audit_entries():
    return [
        {
            'timestamp': '2024-01-15 14:30:25',
            'user': 'etuk@company.com',
            'action': 'Document Signed',
            'workflow': 'WF-001',
            'details': 'Contract signed via DocuSign'
        },
        {
            'timestamp': '2024-01-15 14:15:00',
            'user': 'lawal@company.com',
            'action': 'Approval Granted',
            'workflow': 'WF-002',
            'details': 'Approved budget in Teams'
        },
        {
            'timestamp': '2024-01-15 13:45:00',
            'user': 'admin@company.com',
            'action': 'Workflow Created',
            'workflow': 'WF-003',
            'details': 'New HR policy workflow'
        }
    ]
