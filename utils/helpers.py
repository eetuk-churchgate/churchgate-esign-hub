import requests
import json
import base64
from datetime import datetime
import streamlit as st

def send_docusign_envelope(document_path, recipients, subject="Please Sign"):
    """Send document to DocuSign for real e-signatures"""
    
    # Get keys from Streamlit secrets
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    if not api_key or not account_id:
        return False, "DocuSign not configured in Secrets"
    
    base_url = f"https://{env}/restapi/v2.1/accounts/{account_id}"
    
    # Read document
    try:
        with open(document_path, 'rb') as f:
            document_base64 = base64.b64encode(f.read()).decode('utf-8')
    except:
        return False, "Could not read document file"
    
    # Create envelope
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    envelope = {
        "emailSubject": subject,
        "documents": [{
            "documentBase64": document_base64,
            "name": document_path.split('/')[-1],
            "fileExtension": "pdf",
            "documentId": "1"
        }],
        "recipients": {
            "signers": [{
                "email": r['email'],
                "name": r['name'],
                "recipientId": str(i + 1),
                "routingOrder": str(i + 1)
            } for i, r in enumerate(recipients)]
        },
        "status": "sent"
    }
    
    try:
        response = requests.post(
            f"{base_url}/envelopes",
            headers=headers,
            json=envelope
        )
        
        if response.status_code == 201:
            result = response.json()
            return True, result['envelopeId']
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def get_signing_url(envelope_id, recipient_email, recipient_name):
    """Get embedded signing URL"""
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    base_url = f"https://{env}/restapi/v2.1/accounts/{account_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Create recipient view
    view_request = {
        "returnUrl": st.get_option('server.baseUrlPath') or "https://churchgate-esign.streamlit.app",
        "authenticationMethod": "none",
        "email": recipient_email,
        "userName": recipient_name,
        "clientUserId": recipient_email
    }
    
    response = requests.post(
        f"{base_url}/envelopes/{envelope_id}/views/recipient",
        headers=headers,
        json=view_request
    )
    
    if response.status_code == 201:
        return True, response.json()['url']
    return False, None