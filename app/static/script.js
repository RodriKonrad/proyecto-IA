const chatForm      = document.getElementById('chatForm');
const chatLog       = document.getElementById('chatLog');
const messageInput  = document.getElementById('messageInput');
const errorBox      = document.getElementById('error');
const exampleBtn    = document.getElementById('exampleBtn');
const resetBtn      = document.getElementById('resetBtn');

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderMarkdown(text) {
  const escaped = escapeHtml(text);
  let html = escaped.replace(/```([^\n\r]*)[\n\r]+([\s\S]*?)[\n\r]+```/g, (_, lang, code) => {
    const cls = lang ? ` class="language-${lang.trim()}"` : '';
    return `<pre><code${cls}>${code}</code></pre>`;
  });
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\r\n/g, '\n');
  const paragraphs = html.split(/\n\n+/).map(p => p.replace(/\n/g, '<br>'));
  return paragraphs.join('<br><br>');
}

function appendMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = `<strong>${role === 'user' ? 'Tú' : 'Asesor'}:</strong> ${renderMarkdown(text)}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function showLoading() {
  const div = document.createElement('div');
  div.className = 'msg bot loading';
  div.id = 'loadingMsg';
  div.innerHTML = '<strong>Asesor:</strong> <em>Analizando consulta con el sistema RAG…</em>';
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function removeLoading() {
  const el = document.getElementById('loadingMsg');
  if (el) el.remove();
}

function showError(text) {
  errorBox.textContent = text;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}

// Envío del formulario
chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) { showError('Describe el caso antes de enviar.'); return; }
  hideError();
  appendMessage(text, 'user');
  messageInput.value = '';
  showLoading();

  try {
    const response = await fetch('/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const result = await response.json();
    removeLoading();
    if (!response.ok) { showError(result.error || 'Error inesperado en el servidor.'); return; }
    appendMessage(result.response, 'bot');
  } catch (err) {
    removeLoading();
    showError('No se pudo conectar con el servidor. Revisa la terminal.');
    console.error(err);
  }
});

// Botón de ejemplo
exampleBtn.addEventListener('click', () => {
  messageInput.value = 'Me impusieron un comparendo por pasar un semáforo en rojo, pero aseguro que la luz estaba en amarillo y no había señalización adicional. ¿Qué elementos deben considerarse para evaluar si la multa es válida?';
});

// Botón reset de conversación
resetBtn.addEventListener('click', async () => {
  await fetch('/chat/reset', { method: 'POST' });
  chatLog.innerHTML = '<div class="msg bot"><strong>Asesor:</strong> Conversación reiniciada. Puedes iniciar una nueva consulta.</div>';
  hideError();
});

// Botones de temas rápidos
document.querySelectorAll('.topic').forEach(btn => {
  btn.addEventListener('click', () => {
    messageInput.value = btn.dataset.query || btn.textContent;
    messageInput.focus();
  });
});