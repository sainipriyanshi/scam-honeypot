import os
import random
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

# --- NEW SECTION: The Retry Wrapper ---
# Put this OUTSIDE your main get_ai_response function

api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")

# 2. Configure the SDK
genai.configure(api_key=api_key)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_ai_response(scammer_message, history):

    
    try:
        # 3. Use 1.5-Flash (It is the most stable for project deployments)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 4. Professional System Instructions
        system_prompt = (
            "You are Aman, a 30-year-old customer service target. "
            "Your goal is to act slightly confused and panicked to keep the "
            "scammer talking so we can collect their info. "
            "Keep responses short and realistic."
        )
        
        full_prompt = f"{system_prompt}\n\nScammer says: {scammer_message}\n\nAman:"



        response = model.generate_content(full_prompt)
        response.text
        
        # # 5. Safety Check
        # if response.text:
        #     return response.text
        # return "I am not sure I understand what you want me to do with my bank app."

    except Exception as e:
        # This will log the EXACT reason for the ClientError in your Render logs
        print(f"CRITICAL AI ERROR: {str(e)}")
        raise e