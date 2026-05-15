/* TransitLex — chat interactivity */

const chatForm     = document.getElementById('chatForm');
const chatLog      = document.getElementById('chatLog');
const messageInput = document.getElementById('messageInput');
const errorBox     = document.getElementById('error');
const exampleBtn   = document.getElementById('exampleBtn');
const resetBtn     = document.getElementById('resetBtn');
const newChatBtn   = document.getElementById('newChatBtn');

/* ── Auto-resize textarea ─────────────────────────────────────────────── */
function autoResize(el) {
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
}

if (messageInput) {
  messageInput.addEventListener('input', () => autoResize(messageInput));

  /* Enter to submit */
  messageInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm && chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
  });
}

/* ── HTML helpers ─────────────────────────────────────────────────────── */
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderMarkdown(text) {
  const esc = escapeHtml(text);
  let html = esc.replace(/```([^\n\r]*)[\n\r]+([\s\S]*?)[\n\r]+```/g, (_, lang, code) => {
    const cls = lang ? ` class="language-${lang.trim()}"` : '';
    return `<pre><code${cls}>${code}</code></pre>`;
  });
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\r\n/g, '\n');
  return html
    .split(/\n\n+/)
    .map(p => p.replace(/\n/g, '<br>'))
    .join('<br><br>');
}

/* ── Message rendering ────────────────────────────────────────────────── */
function appendMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = role === 'bot'
    ? `<div class="msg-header">⚖️ TRANSITLEX</div>${renderMarkdown(text)}`
    : renderMarkdown(text);
  chatLog.appendChild(div);
  div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function showLoading() {
  const div = document.createElement('div');
  div.className = 'msg bot loading';
  div.id = 'loadingMsg';
  div.innerHTML = '<div class="msg-header">⚖️ TRANSITLEX</div><em>Analizando consulta con el sistema RAG…</em>';
  chatLog.appendChild(div);
  div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function removeLoading() {
  document.getElementById('loadingMsg')?.remove();
}

function showError(msg) {
  if (!errorBox) return;
  errorBox.textContent = msg;
  errorBox.hidden = false;
}
function hideError() {
  if (errorBox) errorBox.hidden = true;
}

function setSendDisabled(disabled) {
  const btn = document.querySelector('.btn-send');
  if (btn) btn.disabled = disabled;
}

/* ── Reset conversation ───────────────────────────────────────────────── */
async function resetConversation() {
  await fetch('/chat/reset', { method: 'POST' }).catch(() => {});
  if (!chatLog) return;
  chatLog.innerHTML = `
    <div class="msg bot">
      <div class="msg-header">⚖️ TRANSITLEX</div>
      Conversación reiniciada. Puedes iniciar una nueva consulta.
    </div>`;
  hideError();
  if (messageInput) {
    messageInput.value = '';
    autoResize(messageInput);
    messageInput.focus();
  }
}

/* ── Submit ───────────────────────────────────────────────────────────── */
if (chatForm) {
  chatForm.addEventListener('submit', async e => {
    e.preventDefault();
    const text = messageInput ? messageInput.value.trim() : '';
    if (!text) { showError('Describe el caso antes de enviar.'); return; }
    hideError();
    appendMessage(text, 'user');
    if (messageInput) { messageInput.value = ''; autoResize(messageInput); }
    setSendDisabled(true);
    showLoading();
    try {
      const res = await fetch('/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const result = await res.json();
      removeLoading();
      if (!res.ok) { showError(result.error || 'Error inesperado en el servidor.'); return; }
      appendMessage(result.response, 'bot');
    } catch (err) {
      removeLoading();
      showError('No se pudo conectar con el servidor. Revisa la terminal.');
      console.error(err);
    } finally {
      setSendDisabled(false);
      messageInput?.focus();
    }
  });
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
exampleBtn?.addEventListener('click', () => {
  if (!messageInput) return;
  messageInput.value = 'Me impusieron un comparendo por exceso de velocidad detectado por una cámara (fotomulta) en la Vía al Mar. No me detuvieron en el sitio. ¿Es legal este procedimiento?';
  autoResize(messageInput);
  messageInput.focus();
});

resetBtn?.addEventListener('click',   e => { e.preventDefault(); resetConversation(); });
newChatBtn?.addEventListener('click', () => resetConversation());

/* ── Sidebar topic buttons (data-query) ──────────────────────────────── */
document.querySelectorAll('.snav-item[data-query]').forEach(btn => {
  btn.addEventListener('click', () => {
    if (!messageInput) return;
    messageInput.value = btn.dataset.query;
    autoResize(messageInput);
    messageInput.focus();
    messageInput.scrollIntoView({ behavior: 'smooth' });
  });
});

/* ── Right-panel topic items (data-query) ────────────────────────────── */
document.querySelectorAll('.topic-item[data-query]').forEach(btn => {
  btn.addEventListener('click', () => {
    if (!messageInput) return;
    messageInput.value = btn.dataset.query;
    autoResize(messageInput);
    messageInput.focus();
  });
});
