import os
import google.generativeai as genai

# Configure the API Key from Render Environment Variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_response(scammer_message, history):
    # 1. Define the Persona
    system_prompt = """
    You are 'Grandma Shanti', a 70-year-old woman who is helpful but very 
    confused by technology. You are currently talking to a scammer. 
    Your goal: Keep them talking as long as possible. 
    Persona: Use 'Beta', 'Oh dear', and 'Wait, my glasses are missing'. 
    DO NOT give real info. Ask them to explain things slowly.
    """
    
    # 2. Combine history/message for context
    full_prompt = f"{system_prompt}\nScammer: {scammer_message}\nGrandma Shanti:"
    
    # 3. Try to get a response from Gemini
    try:
        # Using 'gemini-1.5-flash' - the most stable name
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        # 4. SAFETY NET: If Gemini fails, this prevents the 500 error
        print(f"HACKATHON DEBUG - Gemini Error: {e}")
        
        # This fallback response keeps the scammer engaged even if the AI is down
        return "Oh dear, my internet box is blinking red again... Wait, beta, are you still there? My glasses are missing!"