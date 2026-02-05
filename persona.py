import os
import random
from google import genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- NEW SECTION: The Retry Wrapper ---
# Put this OUTSIDE your main get_ai_response function
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
def make_api_call(client, model_name, contents):
    """This specific part will retry if it hits a 429 error"""
    return client.models.generate_content(model=model_name, contents=contents)

# --- YOUR MAIN FUNCTION ---
def get_ai_response(scammer_message, history):
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")

    if not api_key:
        return "Arey bhai, please don't block my account! What do I need to do?"

    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are Aman, a worried 30-year-old Indian customer. "
            "A scammer is messaging you. Act panicked and cooperative to lure "
            "them into giving their UPI ID or Bank details. Keep it to 1-2 sentences."
        )

        # Preparing the input
        prompt_content = (
            f"{system_instruction}\n"
            f"Scammer says: '{scammer_message}'\n"
            f"Aman's goal: Be worried but bait them.\n"
            "Reply as Aman:"
        )

        # --- UPDATED CALL ---
        # Instead of calling client.models.generate_content directly, 
        # we call our new retry-protected function.
        response = make_api_call(client, "gemini-1.5-flash", f"Reply to: {scammer_message}")
        
        if response and response.text:
            return response.text
        return "Wait, my screen is stuck."

    except Exception as e:
        # If it still fails after 5 retries, this will catch it
        print(f"Detailed Error: {getattr(e, 'message', str(e))}")
        return "Can you send that again? My phone is hanging."