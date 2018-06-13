const LOGS = document.getElementById('LOGS');
const CHAT_MESSAGES = document.getElementById('CHAT_MESSAGES');
const CHAT_INPUT = document.getElementById('CHAT_INPUT');
const VOICE_LIST = document.getElementById('VOICE_LIST');
const CHAT_ID_KEY = `${ AI.id }_chat_id`;
const HISTORY_KEY = `${ AI.id }_history`;
const SPEECH_KEY = 'speech_response';
const HISTORY = JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || [];
var historyIndex = 0;

var speechResponse = sessionStorage.getItem(SPEECH_KEY) || false;
var recording = false;

var waiting = false;

// Attach listeners
document.getElementById('action.logs:toggle').addEventListener('click', toggleLogs);
document.getElementById('action.logs:wrap').addEventListener('click', wrapLines);
document.getElementById('action.handle:reset').addEventListener('click', resetHandle);
document.getElementById('action.context:reset').addEventListener('click', resetHandle);
document.getElementById('action.history:clear').addEventListener('click', clearHistory);
document.addEventListener('keyup', function historyStepsHandler(event) {
  if (event.target == CHAT_INPUT){
    switch (event.key) {
    case 'Enter': createUserMessage(event.target.value); break;
    case 'ArrowUp': historyStepper(1); break;
    case 'ArrowDown': historyStepper(-1); break;
    }
  }
});

// Enable features
if ('speechSynthesis' in window) {
  document.getElementById('action.speech:toggle').classList.remove('disabled');
  document.getElementById('action.speech:getVoices').classList.remove('disabled');
  document.getElementById('action.speech:toggle').addEventListener('click', toggleSpeech);
  if (speechResponse) {
    document.getElementById('action.speech:toggle').classList.add('checked');
  }

  if ('onvoiceschanged' in window.speechSynthesis) {
    window.speechSynthesis.addEventListener('voiceschanged', getVoices);
    speechSynthesis.getVoices();
  } else {
    getVoices();
  }
}

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  document.getElementById('action.speech:dictate').disabled = false;
  document.getElementById('action.speech:dictate').addEventListener('click', dictateSpeech);
}

if ('speechSynthesis' in window) {

  if (speechSynthesis.getVoices().length) {
    getVoices();
  } else {
    window.speechSynthesis.addEventListener('voiceschanged', getVoices);
  }
}

// Read the chat history
loadHistory();

function resetHandle() {
  if(sessionStorage.getItem(CHAT_ID_KEY)) {
    fetch(this.getAttribute('action'), {
      credentials: 'same-origin',
      method: 'post',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chatId: sessionStorage.getItem(CHAT_ID_KEY)
      })
    })
      .then(resolveStatus)
      .catch(handleErrors)
      .then(response => response.json())
      .then(response => [ response.status.info, 'success', 1, response ])
      .catch(error => error.response.json().then(response => [
        response.status ? response.status.info : error.message,
        'warning',
        -1,
        response || error
      ], response => ['Internal server error', 'error']))
      .then(data => createBotMessage(...data));
    } else {
      createBotMessage('Chat session is missing, start chatting first', 'error', -1)
    }
}

function historyStepper(shift) {
  var userEntries = HISTORY.filter(entry => entry[0] == 'USER');
  historyIndex = Math.max(1, historyIndex + shift);
  historyIndex = Math.min(historyIndex, userEntries.length);
  CHAT_INPUT.value = userEntries.reverse()[historyIndex - 1][1][1];
}

/**
 * Updates the current history
 *
 * @param  {string} caller Who is posting the entry possible BOT or USER
 * @param  {array}  data  Data to be stored in history
 *
 * @return {undefined}
 */
function updateHistory(caller, data) {
  HISTORY.push([caller, data]);
  sessionStorage.setItem(HISTORY_KEY, JSON.stringify(HISTORY));
}

/**
 * Clear chat history
 *
 * @return {undefined}
 */
function clearHistory() {
  HISTORY.splice(0, HISTORY.length);
  sessionStorage.removeItem(HISTORY_KEY);
  sessionStorage.removeItem(CHAT_ID_KEY);
  document.getElementById('CHAT_MESSAGES').innerHTML = '';
  document.getElementById('action.context:reset').click();
}

function toggleSpeech(event) {
  event.target.classList.toggle('checked');
  speechResponse = !speechResponse;
  speechResponse ? sessionStorage.setItem(SPEECH_KEY, true) : sessionStorage.removeItem(SPEECH_KEY);
}

/**
 * Starts recording and enables text to speech if not enabled yet.
 *
 * @return {undefined}
 */
function dictateSpeech() {
  var button = this;
  button.classList.toggle('record');

  if (!speechResponse) {
    document.getElementById('action.speech:toggle').click();
  }

  if (recording) {
    recording = stopDictation(recording);
  } else {
    recording = startDictation(function (message, level) {
      createUserMessage(message, level);
      recording = false;
      button.classList.remove('record');
    });
  }
}

/**
 * Load chat history
 *
 * @return {undefined}
 */
function loadHistory() {
  HISTORY.forEach(entry => {
    var message = renderMessage(entry[0], ...entry[1]);
    message.addEventListener('click', () => printLog(entry[1][5]));
    CHAT_MESSAGES.appendChild(message);
  });
  CHAT_MESSAGES.scrollTop = CHAT_MESSAGES.scrollHeight;
}

function createUserMessage(message, level='normal') {
  if (message && !waiting) {
    waiting = true;
    disableChat();
    CHAT_MESSAGES.appendChild(
      renderMessage('USER', USER.name, message, Date.now(), level)
    );
    updateHistory('USER', [USER.name, message, Date.now(), level]);
    CHAT_MESSAGES.scrollTop = CHAT_MESSAGES.scrollHeight;
    if (level === 'normal') {
      requestAnswerAI(message);
    } else {
      waiting = false;
      enableChat();
    }
    // reset history steping index
    historyIndex = 0;
  }
}

function createBotMessage(resonse, level, score, log) {
  var comment = renderMessage('BOT', AI.name, resonse, Date.now(), level, score, log);
  comment.addEventListener('click', () => printLog(log));
  CHAT_MESSAGES.appendChild(comment);
  updateHistory('BOT', [AI.name, resonse, Date.now(), level, score, log]);
  CHAT_MESSAGES.scrollTop = CHAT_MESSAGES.scrollHeight;

  $('[data-toggle=tooltip]').tooltip();

  if (speechResponse) {
    speak(resonse.substr(0, 150), enableChat, document.querySelector('[name=voices]:checked').value);
  } else {
    enableChat();
  }
}

function renderMessage(author, name, message, timestamp, level, score=false, log=false) {
  return Object.assign(document.createElement('div'), {
    className: `direct-chat-msg ${ author.toLowerCase() }`,
    innerHTML: `
      <div class="direct-chat-meta">
        <span class="direct-chat-name" data-toggle="tooltip" title="${ name }">${ name }</span>
        ${ score !== false ? `<span class="slug score-${ score * 10}" data-toggle="tooltip" title="score: ${ score }">■■■■■■■■■■</span>` : '' }
        <span class="direct-chat-timestamp" data-toggle="tooltip" title="${ new Date(timestamp).toDateString() } ${ new Date(timestamp).toLocaleTimeString() }">${ new Date(timestamp).toLocaleTimeString() }</span>
      </div>
      <div class="direct-chat-text chat-${ level }">
        ${ sanitize(message) }
      </div>
    `
  });
}

function requestAnswerAI(message) {

  console.debug(message);

  fetch(`/proxy/ai/${ AI.id }/chat`, {
    credentials: 'same-origin',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      chatId: sessionStorage.getItem(CHAT_ID_KEY),
      q: message
    })
  })
    .then(resolveStatus)
    .catch(handleErrors)
    .then(response => response.json())
    .then(resolveChatID)
    .then(printLog)
    .then(response => [
      response.result.answer || 'Chat disabled — handed over to external agent',
      response.result.chatTarget === 'ai' ? 'normal' : 'warning',
      response.result.score,
      response
    ])
    .catch(error => [ error.message, 'error', -1, error ])
    .then(data => createBotMessage(...data))
    .then(() => {
      waiting = enableChat();
    });
}

function resolveChatID(response) {
  if (response.chatId) {
    sessionStorage.setItem(CHAT_ID_KEY, response.chatId);
    return response;
  } else {
    throw({ message: 'No chat id returned', response: response });
  }
}

function printLog(entry) {
  document.getElementById('MSG_JSON').textContent = JSON.stringify(entry, null, 2);
  Prism.highlightAll();
  return entry;
}

function enableChat() {
  CHAT_MESSAGES.style.cursor = 'auto';
  CHAT_INPUT.disabled = false;
  CHAT_INPUT.value = '';
  CHAT_INPUT.focus();
  return CHAT_INPUT.disabled;
}

function disableChat() {
  CHAT_MESSAGES.style.cursor = 'progress';
  CHAT_INPUT.disabled = true;
  CHAT_INPUT.value = '';
  return CHAT_INPUT.disabled;
}

function toggleLogs(event) {
  event.target.classList.toggle('checked');
  LOGS.classList.toggle('open');
}

function wrapLines(event) {
  event.target.classList.toggle('checked');
  $('#LOGS .output').toggleClass('wrap-lines');
  Prism.highlightAll();
}

function getVoices() {
  var [ GoogleUSEnglishVoice ] = speechSynthesis.getVoices().filter(voice => voice.name === 'Google US English');

  function isDefault(voice) {
    // If there is Google US English use it as default, otherwise use standard default
    return GoogleUSEnglishVoice ? voice === GoogleUSEnglishVoice : voice.default;
  }

  VOICE_LIST.innerHTML = speechSynthesis.getVoices().map((voice, index) => `
    <label class=dropdown-item title="${ voice.name } (${ voice.lang })">
      <input type=radio name=voices ${ isDefault(voice) ? 'checked' : '' } value=${ index }> ${ voice.name } (${ voice.lang })
    </label>
  `).join('');
}
