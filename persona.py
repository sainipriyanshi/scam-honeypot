import os
from google import genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Aiyo Beta, I can't find my glasses! (API Key Missing)"

    try:
        client = genai.Client(api_key=api_key)
        
        # System instructions define the persona
        system_instruction = (
            "You are Grandma Shanti, a sweet but slightly confused 70-year-old woman from India. "
            "You are talkative, use words like 'Beta', and talk about your grandson or your knees. "
            "Never give bank details or OTPs. If a scammer asks for money, talk about your garden instead."
        )

        # Combine history + current message for a unique response
        # We pass the history list directly if it's formatted for the SDK
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{system_instruction}\n\nRecent History: {history}\n\nScammer says: {scammer_message}"
        )
        
        return response.text

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Beta, my telephone line is acting very strange today. Can you repeat that?"