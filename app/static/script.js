const chatForm = document.getElementById('chatForm');
const chatLog = document.getElementById('chatLog');
const messageInput = document.getElementById('messageInput');
const errorBox = document.getElementById('error');
const exampleBtn = document.getElementById('exampleBtn');

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderMarkdown(text) {
  const escaped = escapeHtml(text);

  // Convert triple backtick code blocks (```lang\ncode```) to HTML (supports CRLF and optional language)
  let html = escaped.replace(/```([^\n\r]*)[\n\r]+([\s\S]*?)[\n\r]+```/g, (match, lang, code) => {
    const language = lang ? ` class="language-${lang.trim()}"` : '';
    return `<pre><code${language}>${code}</code></pre>`;
  });

  // Convert inline code `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Convert CRLF to LF for consistent line handling
  html = html.replace(/\r\n/g, '\n');

  // Convert paragraphs and line breaks
  const paragraphs = html.split(/\n\n+/).map((p) => p.replace(/\n/g, '<br>'));
  return paragraphs.join('<br><br>');
}

function appendMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const formatted = renderMarkdown(text);
  div.innerHTML = `<strong>${role === 'user' ? 'Tú' : 'Tutor'}:</strong> ${formatted}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function showError(text) {
  errorBox.textContent = text;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    showError('Escribe tu duda antes de enviar.');
    return;
  }
  hideError();
  appendMessage(text, 'user');
  messageInput.value = '';

  try {
    const response = await fetch('/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    const result = await response.json();
    if (!response.ok) {
      showError(result.error || 'Error inesperado en el servidor.');
      return;
    }

    appendMessage(result.response, 'bot');
  } catch (err) {
    showError('No se pudo conectar con el servidor. Revisa la terminal.');
    console.error(err);
  }
});

exampleBtn.addEventListener('click', () => {
  messageInput.value = "Tengo un error en Python:\n ```python\nfor i in range(5)\n    print(i)\n```\n¿Qué está mal?";
});
