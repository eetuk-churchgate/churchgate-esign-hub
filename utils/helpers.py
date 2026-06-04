import requests
import json
import base64
from datetime import datetime
import streamlit as st

def send_docusign_envelope(document_path, recipients, subject="Please Sign"):
    """Send document to DocuSign for real e-signatures"""
    
    account_id = st.secrets.get('DOCUSIGN_ACCOUNT_ID', '')
    api_key = st.secrets.get('DOCUSIGN_API_KEY', '')
    env = st.secrets.get('DOCUSIGN_ENV', 'demo.docusign.net')
    
    if not account_id or not api_key:
        return False, "DocuSign not configured in Secrets"
    
    base_url = f"https://{env}/restapi/v2.1/accounts/{account_id}"
    
    try:
        with open(document_path, 'rb') as f:
            document_base64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return False, f"Could not read document: {str(e)}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    envelope = {
        "emailSubject": subject,
        "emailBlurb": "Please review and sign this document.",
        "documents": [{
            "documentBase64": document_base64,
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
            headers=headers,
            json=envelope
        )
        
        if response.status_code == 201:
            result = response.json()
            return True, f"Email sent to {recipients[0]['email']}! Envelope: {result['envelopeId']}"
        else:
            return False, f"Error {response.status_code}: {response.text[:300]}"
    except Exception as e:
        return False, str(e)