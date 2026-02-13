React Frontend<br>
      ↓<br>
FastAPI Backend<br>
      ↓<br>
Gemini 2.5 Flash<br>
      ↓<br>
PostgreSQL Database<br>
<br>
**Flow:**

1. User sends message from frontend

2. Backend receives it

3. Backend sends prompt to Gemini

4. Gemini returns response

5. Backend stores BOTH:

6. user message

7. bot response

8. Data saved in PostgreSQL

9. Backend returns response to frontend


**🔁 How It Works Internally (Step-by-Step)<br>**
1️⃣ User sends message

Frontend:

{
  "message": "I have fever"
}


2️⃣ Backend sends to Gemini

response = model.generate_content(prompt)

3️⃣ Backend saves both messages

INSERT INTO chat_messages (session_id, role, message)
VALUES ('abc123', 'user', 'I have fever');

INSERT INTO chat_messages (session_id, role, message)
VALUES ('abc123', 'assistant', 'Possible causes...');


4️⃣ When user asks again

Backend can fetch history:

SELECT role, message 
FROM chat_messages 
WHERE session_id = 'abc123'
ORDER BY created_at;


**🔄 Conversation Memory Logic**

When storing history, you can:

previous_messages = db.fetch(session_id)

full_prompt = previous_messages + new_user_message


**User Authentication Implementation**<br>

Implemented a secure Signup and Login system using JWT (JSON Web Tokens) for authentication. Users must log in to access the chatbot.

**Database Schema Design**

Added user_id to conversations table. This creates a One-to-Many relationship between User and Conversations.

ERD

<img width="683" height="723" alt="image" src="https://github.com/user-attachments/assets/5740d87c-10a0-4b43-b29b-a7291650a0e8" />


**Models** 
(
models.py
)

[NEW] User

id: Integer, Primary Key<br>
email: String, Unique, Index<br>
hashed_password: String<br>
created_at: DateTime (default now)<br>
conversations: Relationship to <br>
Conversation<br>
[MODIFY] <br>
Conversation<br>

user_id: Integer, ForeignKey("users.id")<br>
owner: Relationship to User<br>

**Authentication Flow**

<img width="761" height="540" alt="image" src="https://github.com/user-attachments/assets/aea7d40c-44ed-4b68-92f1-ab045c63bf3f" />

**Protected Chat Flow**

<img width="734" height="380" alt="image" src="https://github.com/user-attachments/assets/16c2b385-e73e-4e2e-8783-8827ad444c69" />





