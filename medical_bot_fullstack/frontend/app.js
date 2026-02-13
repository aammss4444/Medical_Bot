// Check authentication
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = 'login.html';
}

function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
}
const userPayload = parseJwt(token);
if (userPayload && userPayload.sub) {
    document.getElementById('user-email-display').textContent = userPayload.sub.split('@')[0]; // Show name part
}

const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const logoutBtn = document.getElementById('logout-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const sessionList = document.getElementById('session-list');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const sidebar = document.getElementById('sidebar');

let currentSessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
});

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    sendBtn.disabled = this.value.trim() === '';
});

userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) handleSubmit();
    }
});

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSubmit();
});

logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
});

newChatBtn.addEventListener('click', () => {
    startNewChat();
});

async function loadSessions() {
    try {
        const response = await fetchWithAuth('/sessions');
        if (response.ok) {
            const sessions = await response.json();
            renderSessionList(sessions);
            if (sessions.length > 0 && !currentSessionId) {
                loadSession(sessions[0].id);
            } else if (sessions.length === 0) {
                startNewChat();
            }
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

function renderSessionList(sessions) {
    sessionList.innerHTML = '';
    sessions.forEach((session, index) => {
        const div = document.createElement('div');
        div.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
        // Numbered list style as per reference image (1. Title ...)
        div.innerHTML = `<span>${index + 1}.</span> <span>${escapeHtml(session.title)}</span>`;
        div.onclick = () => loadSession(session.id);
        sessionList.appendChild(div);
    });
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    // Update active class
    const items = document.querySelectorAll('.session-item');
    items.forEach((item, index) => {
        // Simple visual update, ideally re-render from state but this works for click
        if (item.onclick.toString().includes(sessionId)) item.classList.add('active'); // fallback
        // Better: loop sessions data. But standard re-fetch is safer for consistency
    });
    // Just re-fetch list to update active state easily
    const response = await fetchWithAuth('/sessions');
    if (response.ok) renderSessionList(await response.json());

    chatContainer.innerHTML = '';

    try {
        const res = await fetchWithAuth(`/sessions/${sessionId}/messages`);
        if (res.ok) {
            const messages = await res.json();
            messages.forEach(msg => {
                addMessage(msg.content, msg.role === 'User' ? 'user' : 'ai');
            });
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

async function startNewChat() {
    currentSessionId = null;
    chatContainer.innerHTML = '';
    // Deselect all
    const items = document.querySelectorAll('.session-item');
    items.forEach(item => item.classList.remove('active'));
}

async function createSession() {
    try {
        const response = await fetchWithAuth('/sessions', { method: 'POST' });
        if (response.ok) {
            const session = await response.json();
            return session.id;
        }
    } catch (error) {
        console.error('Error creating session:', error);
    }
    return null;
}

async function handleSubmit() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;
    addMessage(message, 'user');

    let sessionId = currentSessionId;
    if (!sessionId) {
        sessionId = await createSession();
        if (!sessionId) {
            addMessage("Error creating chat session.", 'ai', true);
            return;
        }
        currentSessionId = sessionId;
        // Refresh sidebar to show new session
        loadSessions();
    }

    const loadingId = addLoading();

    try {
        const response = await fetchWithAuth('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message, session_id: sessionId })
        });

        const data = await response.json();
        removeLoading(loadingId);

        if (data.reply) {
            addMessage(data.reply, 'ai');
            loadSessions(); // Update title
        } else {
            addMessage("Error: " + (data.detail || "Unknown error"), 'ai', true);
        }

    } catch (error) {
        removeLoading(loadingId);
        addMessage("Details: " + error.message, 'ai', true);
    }
}

async function fetchWithAuth(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    const response = await fetch(`http://127.0.0.1:8001${url}`, { ...options, headers });
    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }
    return response;
}

function addMessage(text, sender, isError = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;

    // Timestamp for reference style
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    msgDiv.innerHTML = `
        <div class="message-bubble">
            ${sender === 'ai' ? parseMarkdown(text) : escapeHtml(text)}
            <span class="message-time">${time} <i class="fa-solid fa-check"></i></span>
        </div>
    `;

    if (isError) {
        msgDiv.querySelector('.message-bubble').style.backgroundColor = '#fed7d7';
        msgDiv.querySelector('.message-bubble').style.color = '#c53030';
    }

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addLoading() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    msgDiv.id = id;
    msgDiv.innerHTML = `
        <div class="message-bubble">
            <i class="fa-solid fa-ellipsis fa-fade"></i>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function parseMarkdown(text) {
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/- /g, '<br>• ');
    html = html.replace(/\n/g, '<br>');
    return html;
}
