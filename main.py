import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()


API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title=" Medical ChatBot", page_icon="🏥")

st.title("Medical ChatBot")

st.markdown( """
⚠️ DISCLAIMER:
This chatbot provides general health information only.
It is NOT a substitute for professional medical advice.
Always consult a qualified doctor for serious conditions.
"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask a question about your health")

if user_input:
    st.session_state.messages.append(("user", user_input))

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

    try:
        response = model.generate_content(prompt)
        reply = response.text

    except Exception as e:
        reply = "I'm sorry, I could not provide an answer."

    st.session_state.messages.append(("assistant", reply))

for role, message in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)