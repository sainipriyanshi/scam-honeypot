import requests
import os

# Ensure this data matches the Aman persona strategy
final_payload = {
  "sessionId": "wertyu-dfghj-ertyui", # Replace with actual sessionId from your logs
  "scamDetected": True,
  "totalMessagesExchanged": 5, # Update based on actual conversation length
  "extractedIntelligence": {
    "bankAccounts": ["1234567890123456"], # GUVI uses 'bankAccounts', not 'bankDetails'
    "upiIds": ["scammer.fraud@okaxis"],
    "phishingLinks": [],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": ["blocked", "urgent", "verify now"]
  },
  "agentNotes": "Aman (customer persona) successfully lured the scammer into providing banking details by acting confused about the app interface."
}

# The Mandatory Submission URL
url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Headers - GUVI requires your API Key for the submission to be linked to your account
headers = {
    "Content-Type": "application/json",
    "x-api-key": os.getenv("GUVI_SECRET_KEY", "YOUR_SECRET_API_KEY") 
}

try:
    print(f"📡 Submitting final results for session {final_payload['sessionId']}...")
    response = requests.post(url, json=final_payload, headers=headers, timeout=10)
    
    print(f"Submission Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        print("✅ SUCCESS: Your intelligence has been recorded by GUVI.")
    else:
        print("❌ ERROR: Submission failed. Check your API key and JSON structure.")

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")