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

@app.post("/chat")
async def chat(msg: Message, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Save User message
    user_msg = models.Conversation(role="User", content=msg.message, owner=current_user)
    db.add(user_msg)
    db.commit()

    # Retrieve recent history for THIS user
    history = db.query(models.Conversation).filter(models.Conversation.user_id == current_user.id).order_by(models.Conversation.created_at.desc()).limit(20).all()
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
        bot_msg = models.Conversation(role="Medical Assistant", content=bot_reply, owner=current_user)
        db.add(bot_msg)
        db.commit()
        
        return {"reply": bot_reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
