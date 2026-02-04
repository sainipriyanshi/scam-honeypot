import re

def extract_raw_intel(text):
    """Uses Regex to find obvious data points aligned with GUVI Section 12 requirements."""
    
    # Combined text to scan (latest message + history)
    # The regex below are optimized for Indian scam patterns
    intel = {
        # UPI IDs (e.g., aman@okhdfc)
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        
        # MANDATORY: GUVI expects 'bankAccounts', not 'bankDetails'
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        
        # Phishing Links (Standard URL regex)
        "phishingLinks": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text),
        
        # Phone Numbers (Matches 10-digit Indian numbers starting with 6-9)
        "phoneNumbers": re.findall(r'\b[6-9]\d{9}\b', text)
    }
    return intel

def get_scam_score(text):
    """
    Analyzes scam intent. 
    If a scam is detected, it triggers the 'Aman' Agent persona.
    """
    keywords = ["blocked", "verify", "urgent", "immediately", "kyc", "suspended", "bank", "account", "otp", "pan"]
    text_lower = text.lower()
    found = [word for word in keywords if word in text_lower]
    
    # Return detection status and the list of keywords found
    is_scam = len(found) > 0
    return is_scam, found