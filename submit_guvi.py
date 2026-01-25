import requests

# The data you just shared with me
final_payload = {
  "sessionId": "abc123-session-id", # <-- MAKE SURE TO USE THE REAL SESSION ID FROM THE TESTER
  "scamDetected": True,
  "totalMessagesExchanged": 19,
  "extractedIntelligence": {
    "upiIds": ["scammer.fraud@fakebank"],
    "bankDetails": ["1234567890123456", "9876543210"],
    "phishingLinks": [],
    "phoneNumbers": ["123456789012", "9876543210"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer engaged and intelligence gathered via Grandma Shanti persona."
}

# The Mandatory Submission URL
url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

response = requests.post(url, json=final_payload)

print(f"Submission Status: {response.status_code}")
print(f"Response: {response.json()}")