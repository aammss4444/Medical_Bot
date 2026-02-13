React Frontend<br>
      ↓<br>
FastAPI Backend<br>
      ↓<br>
Gemini 2.5 Flash<br>
      ↓<br>
PostgreSQL Database<br>
<br>
Flow:

User sends message from frontend

Backend receives it

Backend sends prompt to Gemini

Gemini returns response

Backend stores BOTH:

user message

bot response

Data saved in PostgreSQL

Backend returns response to frontend
