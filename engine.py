import re

def extract_raw_intel(text):
    """Uses Regex to find obvious data points with hackathon-specific keys."""
    intel = {
        # Changed 'upiIds' to match the camelCase standard
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        
        # Changed 'bankAccounts' to 'bankDetails' as per most GUVI problem statements
        "bankDetails": re.findall(r'\b\d{9,18}\b', text),
        
        # This matches the 'phishingLinks' key you saw in the Tester output
        "phishingLinks": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text),
        
        # Added for extra points
        "phoneNumbers": re.findall(r'\+?\d{10,12}', text)
    }
    return intel

def get_scam_score(text):
    """Quick check for urgency keywords."""
    keywords = ["blocked", "verify", "urgent", "immediately", "kyc", "suspended", "bank", "account"]
    found = [word for word in keywords if word in text.lower()]
    return len(found) > 0, found