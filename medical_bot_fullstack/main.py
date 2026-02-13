from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

load_dotenv()

API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

models.Base.metadata.create_all(bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(msg: Message, db: Session = Depends(get_db)):
    # Save User message
    user_msg = models.Conversation(role="User", content=msg.message)
    db.add(user_msg)
    db.commit()

    # Retrieve recent history (limiting to last 20 messages to fit token limits)
    history = db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).limit(20).all()
    # Reverse to chronological order
    history = history[::-1]
    
    # Format history for the prompt
    history_text = "\n".join([f"{entry.role}: {entry.content}" for entry in history])

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
    
    Conversation History:
    {history_text}

    User Symptoms: {msg.message}
    """

    try:
        response = model.generate_content(prompt)
        bot_reply = response.text
        
        # Save Bot response
        bot_msg = models.Conversation(role="Medical Assistant", content=bot_reply)
        db.add(bot_msg)
        db.commit()
        
        return {"reply": bot_reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
