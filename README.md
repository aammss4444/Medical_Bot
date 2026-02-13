# Medical Aid - AI Powered Health Assistant

**Medical Aid** is a full-stack web application designed to provide intelligent, AI-powered health assistance. Built with FastAPI and vanilla JavaScript, it features a modern, responsive UI inspired by leading chat interfaces, offering secure user authentication and persistent conversation history.

## 🚀 Key Features

*   **Intelligent Medical Chatbot**: Powered by Google's **Gemini AI**, providing accurate and context-aware medical information.
*   **Secure Authentication**: Robust Signup and Login system using **JWT (JSON Web Tokens)** and password hashing.
*   **Multi-Session Management**: Create, view, and manage multiple chat sessions. History is saved automatically.
*   **Modern UI/UX**:
    *   **Dark Sidebar / Light Chat**: A clean, professional aesthetic for comfortable reading.
    *   **Mobile Responsive**: Fully functional on mobile devices with a collapsible sidebar.
    *   **Real-time Feedback**: Typing indicators and error handling.
*   **Database Integration**: Built with SQLAlchemy, supporting SQLite (default) and PostgreSQL.

## 🛠️ Technology Stack

*   **Frontend**: HTML5, CSS3 (Custom Properties, Flexbox), JavaScript (ES6+), FontAwesome.
*   **Backend**: Python 3.10+, FastAPI.
*   **Database**: SQLite (Development), SQLAlchemy ORM.
*   **AI Engine**: Google Gemini API (`google-generativeai`).
*   **Authentication**: OAuth2 with Password Flow, OOP-based JWT handling.

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/medical-bot-fullstack.git
    cd medical-bot-fullstack
    ```

2.  **Set Up Virtual Environment** (Recommended)
    ```bash
    python -m venv backend/venv
    # Windows
    backend\venv\Scripts\activate
    # Mac/Linux
    source backend/venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    DATABASE_URL=sqlite:///./medical_bot.db
    SECRET_KEY=your_super_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    API_KEY=your_google_gemini_api_key
    ```

5.  **Run the Application**
    Start the backend server:
    ```bash
    uvicorn main:app --reload --port 8001
    ```

6.  **Access the App**
    Open your browser and navigate to:
    [http://127.0.0.1:8001](http://127.0.0.1:8001)

## 📂 Project Structure

```
medical-bot-fullstack/
├── backend/            # Virtual environment
├── frontend/           # Frontend assets (HTML, CSS, JS)
│   ├── index.html      # Main chat interface
│   ├── login.html      # Login page
│   ├── signup.html     # Signup page
│   ├── style.css       # Global styles
│   └── app.js          # Chat logic
├── main.py             # FastAPI entry point & API routes
├── models.py           # SQLAlchemy database models
├── auth.py             # Authentication utilities
├── database.py         # Database connection setup
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 🔐 Accounts
Since the database is local to your environment, you will need to **Sign Up** on first run to create an account. The first user created will have full access to their own private chat sessions.

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📄 License
This project is open-source and available under the simple **MIT License**.
