React Frontend<br>
      ↓<br>
FastAPI Backend<br>
      ↓<br>
Gemini 2.5 Flash<br>
      ↓<br>
PostgreSQL Database<br>
<br>
Flow:

1. User sends message from frontend

2. Backend receives it

3. Backend sends prompt to Gemini

4. Gemini returns response

5. Backend stores BOTH:

6. user message

7. bot response

8. Data saved in PostgreSQL

9. Backend returns response to frontend


🔁 How It Works Internally (Step-by-Step)<br>
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


🔄 Conversation Memory Logic

When storing history, you can:

previous_messages = db.fetch(session_id)

full_prompt = previous_messages + new_user_message
