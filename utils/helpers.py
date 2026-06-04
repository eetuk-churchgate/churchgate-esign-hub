import requests
import json
import base64
from datetime import datetime
import streamlit as st

def get_docusign_token():
    """Get OAuth token from DocuSign"""
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    secret_key = st.secrets.get('DOCUSIGN_SECRET_KEY', '')
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    if not api_key or not secret_key:
        return None, "Missing DocuSign credentials in Secrets"
    
    # Get JWT token
    url = f"https://account-d.docusign.com/oauth/token"
    
    # For JWT grant, we need to create assertion
    import jwt
    import time
    
    current_time = int(time.time())
    
    # Create JWT assertion
    assertion = {
        "iss": api_key,
        "sub": account_id,
        "aud": "account-d.docusign.com",
        "iat": current_time,
        "exp": current_time + 3600,
        "scope": "signature impersonation"
    }
    
    headers = {"alg": "RS256", "typ": "JWT"}
    
    # This requires RSA private key - for now use simple auth
    # Fallback to basic auth with integration key
    auth_string = f"{api_key}:{secret_key}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    response = requests.post(
        url,
        headers={
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": "signature impersonation"
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access_token'), None
    else:
        return None, response.text

def send_docusign_envelope(document_path, recipients, subject="Please Sign"):
    """Send document to DocuSign for real e-signatures"""
    
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    if not account_id:
        return False, "DocuSign Account ID not configured in Secrets"
    
    # Get OAuth token
    token, error = get_docusign_token()
    if not token:
        return False, f"Authentication failed: {error}"
    
    base_url = f"https://{env}/restapi/v2.1/accounts/{account_id}"
    
    # Read document
    try:
        with open(document_path, 'rb') as f:
            document_base64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return False, f"Could not read document: {str(e)}"
    
    # Create envelope
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    envelope = {
        "emailSubject": subject,
        "emailBlurb": "Please review and sign this document.",
        "documents": [{
            "documentBase64": document_base64,
            "name": document_path.split('/')[-1].split('\\')[-1],
            "fileExtension": "pdf",
            "documentId": "1"
        }],
        "recipients": {
            "signers": [{
                "email": r['email'],
                "name": r['name'],
                "recipientId": str(i + 1),
                "routingOrder": str(i + 1),
                "tabs": {
                    "signHereTabs": [{
                        "documentId": "1",
                        "pageNumber": "1",
                        "xPosition": "100",
                        "yPosition": "100"
                    }]
                }
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
            envelope_id = result['envelopeId']
            return True, f"Envelope sent! ID: {envelope_id}. Check your email at {recipients[0]['email']}"
        else:
            return False, f"API Error: {response.text[:200]}"
    except Exception as e:
        return False, str(e)