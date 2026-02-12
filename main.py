import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

DISCLAIMER = """
⚠️ DISCLAIMER:
This chatbot provides general health information only.
It is NOT a substitute for professional medical advice.
Always consult a qualified doctor for serious conditions.
"""
print(DISCLAIMER)
print("\n🏥 Medical ChatBot (Enter 'exit' to quit.)\n")


def medical_bot(user_input):
    prompt = f""" 
    You are a helpful medical assistant. 
    1. Please provide accurate and concise medical information.
    2. If serious medical condition is suspected, please provide a referral to a medical professional.
    3. Do not provide any personal information.
    4. Do not prescribe any medicines.
    5. Provide structured respons
    e.
        - symptoms
        - possible causes
        - recommended actions
        - next steps
    User Symptoms: {user_input}
    """
    response = model.generate_content(prompt)
    return response.text

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Stay healthy")
        break

    try:
        reply = medical_bot(user_input)
        print("\nBot:\n",reply)
        print("\n" + "-"*50 + "\n")

    except Exception as e:
        print("Error:", e)
