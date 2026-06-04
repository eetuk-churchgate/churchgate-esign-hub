import requests
import json
import base64
from datetime import datetime
import streamlit as st

def get_docusign_token():
    """Get OAuth token using client credentials"""
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    secret_key = st.secrets.get('DOCUSIGN_SECRET_KEY', '')
    
    if not api_key or not secret_key:
        return None, "Missing credentials"
    
    # Encode client_id:client_secret
    auth_string = f"{api_key}:{secret_key}"
    encoded = base64.b64encode(auth_string.encode()).decode()
    
    response = requests.post(
        "https://account-d.docusign.com/oauth/token",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": "signature"
        }
    )
    
    if response.status_code == 200:
        return response.json().get('access_token'), None
    return None, response.text

def send_docusign_envelope(document_path, recipients, subject="Please Sign"):
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    if not account_id:
        return False, "Account ID not configured"
    
    token, error = get_docusign_token()
    if not token:
        return False, f"Auth failed: {error}"
    
    base_url = f"https://{env}/restapi/v2.1/accounts/{account_id}"
    
    try:
        with open(document_path, 'rb') as f:
            doc_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return False, str(e)
    
    envelope = {
        "emailSubject": subject,
        "emailBlurb": "Please review and sign this document.",
        "documents": [{
            "documentBase64": doc_b64,
            "name": "document.pdf",
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
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=envelope
        )
        
        if response.status_code == 201:
            return True, f"✅ Sent! Envelope: {response.json()['envelopeId']}"
        return False, f"Error: {response.text[:300]}"
    except Exception as e:
        return False, str(e)