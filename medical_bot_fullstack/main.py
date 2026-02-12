from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Message):

    prompt = f""" 
    You are a helpful medical assistant. 
    1. Please provide accurate and concise medical information.
    2. If serious medical condition is suspected, please provide a referral to a medical professional.
    3. Do not provide any personal information.
    4. Do not prescribe any medicines.
    5. Provide structured response.
        - symptoms
        - possible causes
        - recommended actions
        - next steps
    User Symptoms: {msg.message}
    """

    try:
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
