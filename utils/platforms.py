import streamlit as st

class PlatformManager:
    def __init__(self):
        self.platforms = {
            'docusign': {
                'name': 'DocuSign',
                'icon': '📝',
                'connected': True,
                'features': ['Templates', 'Bulk Send', 'PowerForms']
            },
            'hellosign': {
                'name': 'HelloSign',
                'icon': '✍️',
                'connected': True,
                'features': ['Embedded Signing', 'Audit Trail', 'API Access']
            },
            'ms365': {
                'name': 'Microsoft 365',
                'icon': '🔷',
                'connected': True,
                'features': ['Teams Integration', 'SharePoint', 'Outlook']
            },
            'google': {
                'name': 'Google Sign',
                'icon': '📱',
                'connected': False,
                'features': ['Gmail Integration', 'Drive Storage', 'Mobile']
            }
        }
    
    def get_connected_platforms(self):
        return [p for p, details in self.platforms.items() if details['connected']]
    
    def get_platform_names(self):
        return [details['name'] for details in self.platforms.values() if details['connected']]
