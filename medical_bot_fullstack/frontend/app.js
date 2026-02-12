const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    sendBtn.disabled = this.value.trim() === '';
});

// Handle Enter key to send
userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) {
            handleSubmit();
        }
    }
});

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSubmit();
});

clearBtn.addEventListener('click', () => {
    // Keep only the welcome message
    const welcome = document.querySelector('.welcome-message');
    chatContainer.innerHTML = '';
    chatContainer.appendChild(welcome);
});

async function handleSubmit() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add User Message
    addMessage(message, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Add Loading Indicator
    const loadingId = addLoading();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove Loading
        removeLoading(loadingId);

        // Add Bot Response
        // Since the backend returns raw text with markdown-like structure
        // We can do simple formatting or just display it
        // Ideally use a markdown parser, but for now we format line breaks
        const formattedReply = formatResponse(data.reply);
        addMessage(formattedReply, 'ai');

    } catch (error) {
        removeLoading(loadingId);
        addMessage("Details: " + error.message, 'ai', true);
    }
}

function addMessage(text, sender, isError = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;

    const icon = sender === 'user' ? 'fa-user' : 'fa-user-doctor';

    // Formatting text for HTML display safely
    // simple conversion of newlines to <br> for basic text
    // The backend returns structured text, so we preserve whitespace style

    let contentHtml = text;
    if (sender === 'ai' && !isError) {
        // Simple markdown-ish parsing for bold and lists if needed, 
        // or just use pre-wrap style via CSS (already handled by markdown-like structure in prompt)
        // We will wrap in a div that handles white-space: pre-wrap
    }

    // Using innerHTML with simple sanitation for basic display or strictly textContent
    // Here we construct DOM elements for safety

    msgDiv.innerHTML = `
        <div class="avatar">
            <i class="fa-solid ${icon}"></i>
        </div>
        <div class="message-content">
            ${sender === 'ai' ? parseMarkdown(text) : escapeHtml(text)}
            ${isError ? '<div class="disclaimer"><i class="fa-solid fa-triangle-exclamation"></i> Error connecting to server.</div>' : ''}
        </div>
    `;

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addLoading() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    msgDiv.id = id;
    msgDiv.innerHTML = `
        <div class="avatar">
            <i class="fa-solid fa-user-doctor"></i>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
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
    // Very basic formatting for the specific bot output structure
    let html = escapeHtml(text);

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Lists
    html = html.replace(/- /g, '<br>• ');

    // Newlines
    html = html.replace(/\n/g, '<br>');

    return html;
}

function formatResponse(text) {
    return text;
}
