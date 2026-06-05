import requests
import json
import base64
import jwt
import time
from datetime import datetime
import streamlit as st

def get_docusign_token():
    """Get JWT token from DocuSign"""
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    user_id = st.secrets.get('DOCUSIGN_USER_ID', '')
    private_key = st.secrets.get('DOCUSIGN_RSA_PRIVATE_KEY', '')
    
    if not api_key or not user_id or not private_key:
        return None, "Missing credentials in Secrets"
    
    # Create JWT assertion
    current_time = int(time.time())
    payload = {
        "iss": api_key,
        "sub": user_id,
        "aud": "account-d.docusign.com",
        "iat": current_time,
        "exp": current_time + 3600,
        "scope": "signature impersonation"
    }
    
    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        
        response = requests.post(
            "https://account-d.docusign.com/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": token
            }
        )
        
        if response.status_code == 200:
            return response.json().get('access_token'), None
        return None, f"JWT Error: {response.text}"
    except Exception as e:
        return None, str(e)

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
    except:
        return False, "Cannot read file"
    
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
                "recipientId": str(i+1)
            } for i, r in enumerate(recipients)]
        },
        "status": "sent"
    }
    
    try:
        response = requests.post(
            f"{base_url}/envelopes",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=envelope
        )
        if response.status_code == 201:
            return True, f"Sent! ID: {response.json()['envelopeId']}"
        return False, response.text[:300]
    except Exception as e:
        return False, str(e)