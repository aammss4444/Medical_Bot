from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
from jose import JWTError, jwt

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Message(BaseModel):
    message: str

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_session = models.ChatSession(owner=current_user)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title, "created_at": new_session.created_at}

@app.get("/sessions")
def get_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == current_user.id).order_by(models.ChatSession.created_at.desc()).all()
    # Return formatted date or just let frontend handle
    return [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]

@app.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(models.Conversation).filter(models.Conversation.session_id == session_id).order_by(models.Conversation.created_at.asc()).all()
    return [{"role": m.role, "content": m.content} for m in messages]

class ChatRequest(BaseModel):
    message: str
    session_id: int

@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == request.session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update title if it's the first message (or generic title)
    if session.title == "New Chat":
        new_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        session.title = new_title
        db.add(session)

    # Save User message
    user_msg = models.Conversation(role="User", content=request.message, session=session, owner=current_user)
    db.add(user_msg)
    db.commit()

    # Retrieve local history for context from DB
    history = db.query(models.Conversation).filter(models.Conversation.session_id == session.id).order_by(models.Conversation.created_at.desc()).limit(20).all()
    history = history[::-1]
    
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

    User Symptoms: {request.message}
    """

    try:
        response = model.generate_content(prompt)
        bot_reply = response.text
        
        # Save Bot response
        bot_msg = models.Conversation(role="Medical Assistant", content=bot_reply, session=session, owner=current_user)
        db.add(bot_msg)
        db.commit()
        
        return {"reply": bot_reply, "title": session.title}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

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
        bot_msg = models.Conversation(role="Medical Assistant", content=bot_reply, owner=current_user)
        db.add(bot_msg)
        db.commit()
        
        return {"reply": bot_reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
