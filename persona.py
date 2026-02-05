import os
import random
import google.generativeai as genai
from google.api_core import exceptions

def get_ai_response(scammer_message, history):
    # 1. Setup fallback responses just in case
    fallback_responses = [
        "Arey bhai, please don't block my account! What do I need to do?",
        "I am trying to open the app but it is very slow. Can you help me?",
        "Which SBI branch are you calling from? I will come there tomorrow.",
        "Oh no! My wife will be so angry if the account is blocked. Please wait.",
        "I am typing the OTP but it says invalid. Can you send it again?"
    ]

    api_key = os.getenv("GEMINI_API_KEY")
    
    # If no API key is found, use the fallback immediately
    if not api_key:
        return random.choice(fallback_responses)
    
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        # New Persona: Aman (Normal Customer)
        # Strategy: Act worried/cooperative to lure the scammer into giving their details.
        prompt = (
            "You are Aman, a regular 30-year-old customer. You just received a message regarding your bank/UPI. "
            "You are slightly panicked but willing to cooperate. "
            "Your goal is to be a 'Honeypot': act like you don't know how to use the app well so the scammer "
            "is forced to give you THEIR Bank Account number, UPI ID, or Phone Number to 'help' you. "
            "Keep your responses concise and realistic. Do not reveal you are an AI."
        )

        response = model.generate_content(prompt)
        # # Formatting the conversation context
        # prompt = f"""
        # System Role: {prompt}
        
        # Conversation History:
        # {history}
        
        # Latest Scammer Message: "{scammer_message}"
        
        # Aman's Response:"""

        # response = client.models.generate_content(
        #     model="gemini-1.5-flash",
        #     contents=f"{system_instruction}\n\nScammer: {scammer_message}\n\nAman:"
        # )
        
        if response and response.text:
            return response.text
        else:
            return random.choice(fallback_responses)

    except Exception as e:
        print(f"Gemini 2.0 Error: {e}")
        return "The connection is weak, could you please send that again?"