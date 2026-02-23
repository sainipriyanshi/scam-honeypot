import re
import json

def extract_raw_intel(text):
    """Uses Regex to find obvious data points."""
    intel = {
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "phishingLinks": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text),
        "phoneNumbers": re.findall(r'\+?\d{10,12}', text)
    }
    return intel

def get_scam_score(text):
    """Quick check for urgency keywords."""
    keywords = ["blocked", "verify", "urgent", "immediately", "kyc", "suspended"]
    found = [word for word in keywords if word in text.lower()]
    return len(found) > 0, found