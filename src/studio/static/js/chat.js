const ASIDE = document.getElementById('ASIDE');
const LOGS = document.getElementById('LOGS');
const CHAT_MESSAGES = document.getElementById('CHAT_MESSAGES');
const CHAT_INPUT = document.getElementById('CHAT_INPUT');
const VOICE_LIST = document.getElementById('VOICE_LIST');
const CHAT_ID_KEY = `${ AI.id }_chat_id`;
const HISTORY_KEY = `${ AI.id }_history`;
const SPEECH_KEY = 'speech_response';
const VOICE_KEY = 'speech_response_voice';
const HISTORY = JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || [];
var historyIndex = 0;

var speechResponse = sessionStorage.getItem(SPEECH_KEY) || false;
var recording = false;

var waiting = false;

const URLS = {
  'studio:intent': {
    path: (aiid, intent) => `/bots/edit/${ aiid }/intents/edit/${ intent }`
  },
  'studio:chat': {
    path: (aiid) => `/proxy/ai/${ aiid }/chat`
  }
}

function url(name, ...arguments) {
  return URLS[name].path(...arguments);
}

// Attach listeners
document.getElementById('CHAT_TOGGLE_WIDE_VIEW').addEventListener('click', toggleWideView);
document.getElementById('LOGS_TOGGLE_ACTION').addEventListener('click', toggleLogs);
document.getElementById('LOGS_WRAP_ACTION').addEventListener('click', wrapLines);
document.getElementById('HANDOVER_RESET_ACTION').addEventListener('click', resetHandle);
document.getElementById('CONTEXT_RESET_ACTION').addEventListener('click', resetHandle);
document.getElementById('HISTORY_CLEAR_ACTION').addEventListener('click', clearHistory);
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
  document.getElementById('SPEECH_TOGGLE_ACTION').classList.remove('disabled');
  document.getElementById('SPEECH_GETVOICES_ACTION').classList.remove('disabled');
  document.getElementById('SPEECH_TOGGLE_ACTION').addEventListener('click', toggleSpeech);
  if (speechResponse) {
    document.getElementById('SPEECH_TOGGLE_ACTION').classList.add('checked');
  }

  if ('onvoiceschanged' in window.speechSynthesis) {
    window.speechSynthesis.addEventListener('voiceschanged', getVoices);
    speechSynthesis.getVoices();
  } else {
    getVoices();
  }
}

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  document.getElementById('SPEECH_DICTATE_ACTION').disabled = false;
  document.getElementById('SPEECH_DICTATE_ACTION').addEventListener('click', dictateSpeech);
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

/**
 * Preparers data for chat message from provided error response
 *
 * @param  {Object} error   Error object thrown during Promise resolving
 * @return {Promise}        Promise that returns array of chat data
 */
function chatErrorHandle(error) {

  // If error response is an JSON object pass it's data to the chat
  function onFulfilled(response) {
    return {
      message: response.status ? response.status.info : error.message,
      level: response.status && response.status.code == 400 ? 'warning' : 'error',
      score: -1,
      log: response || error
    };
  }

  // If error response is anything else provide a fallback error to the chat
  function onRejected(response) {
    return {
      message: 'Internal server error',
      level: 'error',
      score: -1,
      log: response
    };
  }

  return error.response.json().then(onFulfilled, onRejected);

}

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
      .then(response => ({
        message: response.status.info,
        level: 'success',
        score: 1,
        log: response
      }))
      .catch(chatErrorHandle)
      .then(data => createBotMessage(data.message, data.level, data.score, data.log));

    // Trigger GTM event
    if(dataLayer) {
      dataLayer.push({
        event: 'abstractEvent',
        eventCategory: 'action',
        eventAction: 'send',
        eventLabel: this.getAttribute('id'),
        eventMetadata: {
          timestamp: Date.now()
        }
      });
    }
  } else {
    console.warn('Chat session is missing');
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
  document.getElementById('CONTEXT_RESET_ACTION').click();
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
    document.getElementById('SPEECH_TOGGLE_ACTION').click();
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
    // reset history stepping index
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
  var { intents } = {...log.result};
  return Object.assign(document.createElement('div'), {
    className: `direct-chat-msg ${ author.toLowerCase() }`,
    innerHTML: `
      <div class="direct-chat-meta">
        <span class="direct-chat-name" data-toggle="tooltip" title="${ name }">${ name }</span>
        ${ score !== false ? `<span class="slug score-${ score * 10 }" data-toggle="tooltip" title="score: ${ score }">■■■■■■■■■■</span>` : '' }
        <span class="direct-chat-timestamp" data-toggle="tooltip" title="${ new Date(timestamp).toDateString() } ${ new Date(timestamp).toLocaleTimeString() }">${ new Date(timestamp).toLocaleTimeString() }</span>
        <span class="direct-chat-actions">
          ${ intents ? renderIntent(intents[0]) : '' }
        </span>
      </div>
      <div class="direct-chat-text chat-${ level }">
        ${ sanitize(message) }
      </div>
    `
  });
}

function renderIntent(intent) {
  return `<a href="${ url('studio:intent', AI.id, intent.name) }" data-toggle="tooltip" title="Edit ${ intent.name }"><i class="fa fa-sitemap"></i></a>`;
}

function requestAnswerAI(message) {

  console.debug(message);

  /**
   * Displays messages levels, based on incomming response, if the message text
   * is missing we use a custom level empty. By default returns level `normal`
   *
   * @param {object} response   Incomming response from the API
   * @return {string}           Message level
   */
  function setLevel(response) {

    if (!response.result.answer) {
      return 'empty';
    } else if (response.result.chatTarget !== 'ai') {
      return 'warning';
    } else {
      return 'normal';
    }

  }

  fetch(url('studio:chat', AI.id), {
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
    .then(response => ({
      message: response.result.answer || EMPTY_CHAT_MESSAGE,
      level: setLevel(response),
      score: response.result.score,
      log: response
    }))
    .catch(chatErrorHandle)
    .then(data => createBotMessage(data.message, data.level, data.score, data.log))
    .then(() => {
      waiting = enableChat();
    });

  // Trigger GTM event
  if(dataLayer) {
    dataLayer.push({
      event: 'abstractEvent',
      eventCategory: 'action',
      eventAction: 'send',
      eventLabel: 'CHAT_ACTION',
      eventMetadata: {
        timestamp: Date.now()
      }
    });
  }
}

function resolveChatID(response) {
  if (response.chatId) {
    sessionStorage.setItem(CHAT_ID_KEY, response.chatId);
    return response;
  } else {
    throw({ message: 'No chat id returned', response: response });
  }
}

/**
 * Decorates intents if any with links and prints a log using Prism.
 * @param  {Object} entry   Log entry to be printed
 * @return {Object}         Returns log for future needs
 */
function printLog(entry) {
  // We ❤️ Javascript, dirty but efective object cloning
  var newEntry = JSON.parse(JSON.stringify(entry));
  if (newEntry.result && newEntry.result.intents) {
    newEntry.result.intents.forEach(intent => intent.name = `[${ intent.name }](${ location.origin + url('studio:intent', AI.id, intent.name) })`)
  }
  document.getElementById('MSG_JSON').textContent = JSON.stringify(newEntry, null, 2);
  Prism.highlightAll();
  return entry;
}

function toggleWideView(event) {
  event.target.classList.toggle('fa-window-maximize');
  event.target.classList.toggle('fa-window-restore');
  ASIDE.classList.toggle('wide');
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
  event.target.classList.toggle('fa-indent');
  event.target.classList.toggle('fa-outdent');
  $('#LOGS .output').toggleClass('wrap-lines');
}

/**
 * Prepares the voice list and enables one that should be used.
 *
 * @return {undefined}
 */
function getVoices() {
  var voices = speechSynthesis.getVoices();
  var [ GoogleUSEnglishVoice ] = voices.filter(voice => voice.name === 'Google US English');
  var [ defaultVoice ] = voices.filter(voice => voice.default);

  function hashCode(string='') {
    return [...string].reduce(
      (accumulator, currentValue) => (((accumulator << 5) - accumulator) + currentValue.charCodeAt(0)) | 0,
      0
    );
  }

  VOICE_LIST.innerHTML = voices.map((voice, index) => `
    <label class=dropdown-item title="${ voice.name } (${ voice.lang })">
      <input type=radio name=voices id="VOICE_${ hashCode(voice.name) }" value=${ index }> ${ voice.name } (${ voice.lang })
    </label>
  `).join('');

  if (voices.length) {

    // Selected Voice, if there is one selected use it, otherwise if there is a
    // “Google US English” use it, if not use default, finally if neither is available
    // use first one available.
    var voiceId = sessionStorage.getItem(VOICE_KEY) || 'VOICE_' + hashCode((GoogleUSEnglishVoice || defaultVoice || voices[0]).name);

    // Enable chosen voice
    document.getElementById(voiceId).click();
  } else {
    // If there are no voices disable TTS
    document.getElementById('SPEECH_TOGGLE_ACTION').classList.add('disabled');
    document.getElementById('SPEECH_GETVOICES_ACTION').classList.add('disabled');
    document.getElementById('SPEECH_TOGGLE_ACTION').removeEventListener('click', toggleSpeech);
  }

}

VOICE_LIST.addEventListener('change', function(event) {
  if (event.target.value) {
    sessionStorage.setItem(VOICE_KEY, event.target.id);
  }
});
