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

8.Data saved in PostgreSQL

9. Backend returns response to frontend


🔁 How It Works Internally (Step-by-Step)
1️⃣ User sends message

Frontend:

{
  "message": "I have fever"
}
