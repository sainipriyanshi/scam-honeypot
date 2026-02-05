import os
import random
import google.generativeai as genai
from google.api_core import exceptions

# Configure the API Key globally
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(scammer_message, history):
    fallback_responses = [
        "Arey bhai, please don't block my account! What do I need to do?",
        "I am trying to open the app but it is very slow. Can you help me?",
        "Which SBI branch are you calling from? I will come there tomorrow.",
        "Oh no! My wife will be so angry if the account is blocked. Please wait.",
        "I am typing the OTP but it says invalid. Can you send it again?"
    ]

    try:
        # 1. FIXED: Use the correct model initialization (removed genai.Client)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 2. PROMPT: Give Aman a clear personality and goal
        system_instruction = (
            "You are Aman, a regular 30-year-old Indian customer. You just received a scam message. "
            "You are slightly panicked but willing to cooperate. "
            "Your goal: Act like you don't know how to use the app well so the scammer "
            "is forced to provide THEIR Bank Account, UPI ID, or Phone Number to 'help' you. "
            "Keep responses concise (1-2 sentences) and realistic."
        )

        # 3. CONTEXT: Combine history so Aman remembers previous messages
        # This helps the AI understand the flow of the scam
        chat_context = f"{system_instruction}\n\nHistory: {history}\n\nScammer: {scammer_message}\n\nAman:"

        # 4. EXECUTE: Generate the response
        response = model.generate_content(chat_context)
        
        if response and response.text:
            return response.text
        else:
            return random.choice(fallback_responses)

    except Exception as e:
        print(f"Gemini Error: {e}")
        # If the API fails or quota is exhausted, return a realistic 'Aman' fallback
        return random.choice(fallback_responses)