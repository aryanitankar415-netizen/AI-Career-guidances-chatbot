const form = document.getElementById('chatForm');
const input = document.getElementById('messageInput');
const messages = document.getElementById('messages');
const typing = document.getElementById('typing');

function smoothScrollToBottom() {
  messages.scrollTo({
    top: messages.scrollHeight,
    behavior: 'smooth'
  });
}

function addMessage(role, text) {
  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  const avatar = role === 'assistant' ? '🤖' : '👤';

  wrap.innerHTML = `
    <div class="avatar">${avatar}</div>
    <div>
      <b>${role === 'assistant' ? 'CareerGuide AI' : 'You'}</b>
      <p></p>
    </div>
  `;

  wrap.querySelector('p').textContent = text;
  messages.appendChild(wrap);

  // Smooth scroll
  setTimeout(smoothScrollToBottom, 50);
}


/* ==============================
   TYPING INDICATOR
================================ */

function showTyping() {
  if (!typing) return;

  typing.innerHTML = `
    <div class="typing-content">
      <span>🤖</span>
      <b>CareerGuide AI</b>
      <span class="thinking-text">is thinking</span>
      <span class="thinking-dots">
        <i></i>
        <i></i>
        <i></i>
      </span>
    </div>
  `;

  typing.classList.add('show');

  setTimeout(smoothScrollToBottom, 50);
}

function hideTyping() {
  if (!typing) return;

  typing.classList.remove('show');
}


/* ==============================
   SEND MESSAGE
================================ */

async function sendMessage(text) {
  addMessage('user', text);

  input.value = '';
  input.focus();

  showTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Request failed');
    }

    hideTyping();

    addMessage('assistant', data.reply);

  } catch (err) {
    hideTyping();

    addMessage(
      'assistant',
      'Sorry, something went wrong: ' + err.message
    );

  } finally {
    input.focus();
    smoothScrollToBottom();
  }
}


/* ==============================
   FORM SUBMIT
================================ */

form.addEventListener('submit', e => {
  e.preventDefault();

  const text = input.value.trim();

  if (text) {
    sendMessage(text);
  }
});


/* ==============================
   QUICK PROMPTS
================================ */

function usePrompt(text) {
  input.value = text;
  input.focus();

  // Put cursor at the end
  input.setSelectionRange(
    input.value.length,
    input.value.length
  );
}


/* ==============================
   LOAD CHAT HISTORY
================================ */

async function loadHistory() {
  try {
    const res = await fetch('/api/history');

    if (!res.ok) return;

    const history = await res.json();

    if (history.length) {
      messages.innerHTML = '';

      history.forEach(x => {
        addMessage(
          x.role === 'assistant'
            ? 'assistant'
            : 'user',
          x.message
        );
      });

      // Scroll after history loads
      setTimeout(() => {
        messages.scrollTop = messages.scrollHeight;
      }, 100);
    }

  } catch (_) {
    // Ignore history errors
  }
}


/* ==============================
   CLEAR CHAT
================================ */

function clearChat() {
  messages.innerHTML = `
    <div class="message assistant">
      <div class="avatar">🤖</div>
      <div>
        <b>CareerGuide AI</b>
        <p>
          New chat started. What career question can I help you with?
        </p>
      </div>
    </div>
  `;

  smoothScrollToBottom();
  input.focus();
}


/* ==============================
   VOICE INPUT
================================ */

let recognition = null;
let isListening = false;

function setupVoiceInput() {

  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn(
      'Speech Recognition is not supported in this browser.'
    );
    return;
  }

  recognition = new SpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = true;

  // English + Hindi support
  recognition.lang = 'en-IN';

  recognition.onstart = () => {
    isListening = true;

    if (voiceButton) {
      voiceButton.classList.add('listening');
      voiceButton.title = 'Listening...';
    }
  };

  recognition.onresult = event => {

    let transcript = '';

    for (
      let i = event.resultIndex;
      i < event.results.length;
      i++
    ) {
      transcript += event.results[i][0].transcript;
    }

    input.value = transcript;
  };

  recognition.onerror = event => {
    console.log(
      'Voice recognition error:',
      event.error
    );

    stopVoice();
  };

  recognition.onend = () => {
    stopVoice();
  };
}


/* ==============================
   VOICE BUTTON
================================ */

let voiceButton = null;

function createVoiceButton() {

  // Don't create duplicate button
  if (document.getElementById('voiceButton')) {
    voiceButton = document.getElementById('voiceButton');
    return;
  }

  // Find chat form
  if (!form) return;

  voiceButton = document.createElement('button');

  voiceButton.type = 'button';
  voiceButton.id = 'voiceButton';
  voiceButton.className = 'voice-button';
  voiceButton.innerHTML = '🎤';
  voiceButton.title = 'Voice input';

  // Add button at end of form
  form.appendChild(voiceButton);

  voiceButton.addEventListener('click', toggleVoice);
}


function toggleVoice() {

  if (!recognition) {
    alert(
      'Voice input is not supported in this browser. Please use Google Chrome or Microsoft Edge.'
    );
    return;
  }

  if (isListening) {
    recognition.stop();
  } else {

    try {
      recognition.start();
    } catch (error) {
      console.log(error);
    }
  }
}


function stopVoice() {

  isListening = false;

  if (voiceButton) {
    voiceButton.classList.remove('listening');
    voiceButton.innerHTML = '🎤';
    voiceButton.title = 'Voice input';
  }
}


/* ==============================
   INITIALIZE
================================ */

setupVoiceInput();
createVoiceButton();
loadHistory();