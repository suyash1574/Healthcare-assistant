const messagesEl = document.getElementById('messages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const reloadBtn = document.getElementById('reloadBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.querySelector('.sidebar');

let history = [];
let isWaiting = false;

// ── Sidebar toggle (mobile) ──────────────────────────────────────────────────
menuToggle?.addEventListener('click', () => sidebar.classList.toggle('open'));
document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuToggle) {
        sidebar.classList.remove('open');
    }
});

// ── KB Status ────────────────────────────────────────────────────────────────
function setStatus(state, text) {
    statusDot.className = `status-dot ${state}`;
    statusText.textContent = text;
}

async function checkHealth() {
    try {
        const r = await fetch('/health');
        if (r.ok) setStatus('ready', 'Knowledge base ready');
    } catch {
        setStatus('error', 'Server unreachable');
    }
}

async function reloadDocs() {
    setStatus('loading', 'Reloading documents...');
    reloadBtn.disabled = true;
    try {
        const r = await fetch('/ingest', { method: 'POST' });
        const d = await r.json();
        setStatus('ready', `${d.chunks} chunks loaded`);
    } catch {
        setStatus('error', 'Reload failed');
    }
    reloadBtn.disabled = false;
}

// ── Message Helpers ───────────────────────────────────────────────────────────
function hideWelcome() {
    const ws = document.getElementById('welcomeScreen');
    if (ws) ws.style.display = 'none';
}

function time() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function addUserMessage(text) {
    hideWelcome();
    const row = document.createElement('div');
    row.className = 'msg-row user';
    row.innerHTML = `
        <div class="avatar user">You</div>
        <div class="msg-content">
            <div class="bubble user">${escapeHtml(text)}</div>
            <span class="msg-meta">${time()}</span>
        </div>`;
    messagesEl.appendChild(row);
    scrollBottom();
}

function addBotMessage(text, sources = [], confidence = '') {
    const row = document.createElement('div');
    row.className = 'msg-row bot';

    // Sources pills with chunk preview tooltip
    const sourcesHtml = sources.length
        ? `<div class="sources-tag">${sources.map(s =>
            `<span class="source-pill" title="${escapeHtml(s.chunk || '')}">📄 ${s.document.replace('.txt','')}</span>`
          ).join('')}</div>`
        : '';

    // Confidence badge
    const confidenceHtml = (confidence && confidence !== 'none')
        ? `<span class="confidence-badge confidence-${confidence}">${confidence} confidence</span>`
        : '';

    row.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="msg-content">
            <div class="bubble bot">${marked.parse(text)}</div>
            ${sourcesHtml}
            <div class="msg-footer">
                ${confidenceHtml}
                <span class="msg-meta">${time()}</span>
            </div>
        </div>`;
    messagesEl.appendChild(row);
    scrollBottom();
}

function showTyping() {
    hideWelcome();
    const row = document.createElement('div');
    row.className = 'msg-row bot';
    row.id = 'typingRow';
    row.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="msg-content">
            <div class="bubble bot typing-bubble">
                <span></span><span></span><span></span>
            </div>
        </div>`;
    messagesEl.appendChild(row);
    scrollBottom();
}

function removeTyping() {
    document.getElementById('typingRow')?.remove();
}

function scrollBottom() {
    messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Send Question ─────────────────────────────────────────────────────────────
async function sendQuestion(question) {
    if (!question.trim() || isWaiting) return;

    isWaiting = true;
    sendBtn.disabled = true;
    questionInput.value = '';
    autoResize();

    addUserMessage(question);
    showTyping();

    try {
        const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, history })
        });

        removeTyping();

        if (!res.ok) {
            addBotMessage('Sorry, I encountered an error. Please try again.');
        } else {
            const data = await res.json();
            addBotMessage(data.answer, data.sources || [], data.confidence || '');
            history.push({ role: 'user', content: question });
            history.push({ role: 'assistant', content: data.answer });
            if (history.length > 12) history = history.slice(-12);
        }
    } catch {
        removeTyping();
        addBotMessage('Unable to reach the server. Please check if the application is running.');
    }

    isWaiting = false;
    sendBtn.disabled = questionInput.value.trim() === '';
    questionInput.focus();
}

// ── Input auto-resize ─────────────────────────────────────────────────────────
function autoResize() {
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 150) + 'px';
}

questionInput.addEventListener('input', () => {
    autoResize();
    sendBtn.disabled = questionInput.value.trim() === '' || isWaiting;
});

questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuestion(questionInput.value.trim());
    }
});

sendBtn.addEventListener('click', () => sendQuestion(questionInput.value.trim()));

// ── New Chat ──────────────────────────────────────────────────────────────────
newChatBtn.addEventListener('click', () => {
    history = [];
    messagesEl.innerHTML = '';
    const ws = document.createElement('div');
    ws.id = 'welcomeScreen';
    ws.className = 'welcome-screen';
    ws.innerHTML = `
        <div class="welcome-icon">
            <svg width="48" height="48" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="#2563eb"/>
                <path d="M16 8v16M8 16h16" stroke="white" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
        <h2>How can I help you today?</h2>
        <p>I can answer questions about appointments, insurance, medications, telehealth, and healthcare policies.</p>
        <div class="suggestion-grid">
            <button class="suggestion-card" data-q="What documents do I need for my first appointment?"><span class="card-icon">📋</span><span>First appointment requirements</span></button>
            <button class="suggestion-card" data-q="How do I schedule a telehealth visit?"><span class="card-icon">💻</span><span>Schedule telehealth visit</span></button>
            <button class="suggestion-card" data-q="What is the cancellation policy?"><span class="card-icon">❌</span><span>Cancellation policy</span></button>
            <button class="suggestion-card" data-q="How do I request a medication refill?"><span class="card-icon">💊</span><span>Medication refill process</span></button>
        </div>`;
    messagesEl.appendChild(ws);
    bindSuggestionCards();
    sidebar.classList.remove('open');
    questionInput.focus();
});

// ── Quick topics & suggestion cards ──────────────────────────────────────────
function bindSuggestionCards() {
    document.querySelectorAll('.suggestion-card, .topic-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.dataset.q;
            questionInput.value = q;
            autoResize();
            sendBtn.disabled = false;
            sendQuestion(q);
            sidebar.classList.remove('open');
        });
    });
}

reloadBtn.addEventListener('click', reloadDocs);

// ── Init ──────────────────────────────────────────────────────────────────────
bindSuggestionCards();
checkHealth();
questionInput.focus();
