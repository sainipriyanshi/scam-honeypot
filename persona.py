import os
import random
from google import genai  # Ensure this is the 'google-genai' library

def get_ai_response(scammer_message, history):
    # 1. Fallback responses if the API fails or quota hits
    fallback_responses = [
        "Arey bhai, please don't block my account! What do I need to do?",
        "I am trying to open the app but it is very slow. Can you help me?",
        "Which SBI branch are you calling from? I will come there tomorrow.",
        "Wait, I am typing the OTP but it says invalid. Send again?"
    ]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return random.choice(fallback_responses)

    try:
        # 2. Setup the Client
        client = genai.Client(api_key=api_key)
        
        # 3. Create the Persona Prompt
        system_instruction = (
            "You are Aman, a worried 30-year-old Indian customer. "
            "A scammer is messaging you. Act panicked and cooperative to lure "
            "them into giving their UPI ID or Bank details. Keep it to 1-2 sentences."
        )

        # 4. Generate Content using Gemini 3 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Use 2.0 unless you specifically have 3.0 access
            contents=f"{system_instruction}\n\nHistory: {history}\n\nScammer: {scammer_message}\n\nAman:"
        )
        
        if response and response.text:
            return response.text
        return random.choice(fallback_responses)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return random.choice(fallback_responses)