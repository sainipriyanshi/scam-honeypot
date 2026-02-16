import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

# 1. Configuration
api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '')
genai.configure(api_key=api_key)

# 2. Add Persistence (Retry for network issues)
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def get_ai_response(scammer_message, history):
    try:
        # 3. Main Model Attempt
        model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
        response = model.generate_content(
            f"Act as Aman, a confused target. Scammer says: {scammer_message}",
            generation_config={"max_output_tokens": 100, "temperature": 0.7}
        )
        return response.text

    except Exception as e:
        error_msg = str(e).lower()
        print(f"DEBUG: Initial attempt failed: {error_msg}")

        # 4. Fallback Logic (If the model name is wrong)
        if "not found" in error_msg or "404" in error_msg:
            try:
                print("Switching to fallback model: gemini-pro")
                fallback_model = genai.GenerativeModel('gemini-pro')
                return fallback_model.generate_content(scammer_message).text
            except:
                pass

        # 5. Last Resort
        return "Arey, wait... network is very weak here."