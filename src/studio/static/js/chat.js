const LOGS = document.getElementById('LOGS');
const CHAT_MESSAGES = document.getElementById('CHAT_MESSAGES');
const CHAT_INPUT = document.getElementById('CHAT_INPUT');
const VOICE_LIST = document.getElementById('VOICE_LIST');
const CHAT_ID_KEY = `${AI.id}_chat_id`;
const HISTORY_KEY = `${AI.id}_history`;
const HISTORY = JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || [];
var historyIndex = 0;

var speechResponse = false;
var recording = false;

var waiting = false;

// Attach listeners
document.getElementById('action.logs:toggle').addEventListener('click', toggleLogs);
document.getElementById('action.logs:wrap').addEventListener('click', wrapLines);
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

function historyStepper(shift) {
  var userEntries = HISTORY.filter(entry => entry[0] == 'USER');
  historyIndex = Math.max(1, historyIndex + shift);
  historyIndex = Math.min(historyIndex, userEntries.length);
  CHAT_INPUT.value = userEntries.reverse()[historyIndex - 1][1][1];
}

// Enable features
if ('speechSynthesis' in window) {
  document.getElementById('action.speech:toggle').classList.remove('disabled');
  document.getElementById('action.speech:getVoices').classList.remove('disabled');
  document.getElementById('action.speech:toggle').addEventListener('click', toggleSpeech);

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

/**
 * Add Authorization headers to an AJAX call
 *
 * @param  {object} request AJAX call request
 *
 * @return {undefined}
 */
function setAuthorization(request) {
  request.setRequestHeader('Authorization', `Bearer ${ USER.token }`);
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
}

function toggleSpeech(event) {
  event.target.classList.toggle('checked');
  speechResponse = !speechResponse;
}

function dictateSpeech() {
  var button = this;
  button.classList.toggle('record');

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
        ${ score ? `<span class="slug score-${ score * 10}" data-toggle="tooltip" title="score: ${ score }">■■■■■■■■■■</span>` : '' }
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

  $.ajax({
    url: API_URL + `/ai/${ AI.id }/chat`,
    contentType: 'application/json; charset=utf-8',
    beforeSend: setAuthorization,
    data: {
      chatId: sessionStorage.getItem(CHAT_ID_KEY),
      q: message
    },
    complete: function () {
      waiting = false;
      enableChat();
    },
    success: function (response) {

      var level = 'error';
      var message = 'Oops, there was an error…';
      var score = -1;

      if (response) {
        // Write response in JSON message box
        printLog(response);

        if (response.chatId) {
          // save the chatID
          sessionStorage.setItem(CHAT_ID_KEY, response.chatId);

          if (response.status.code == 200) {
            level = 'normal';
            message = response.result.answer;
            score = response.result.score;
          } else {
            message = response.status.info;
          }

        } else {
          message = 'No chat id returned';
        }
      }

      createBotMessage(message, level, score, response);

    },
    error: function (jqXHR, textStatus, errorThrown) {

      console.debug(jqXHR, textStatus, errorThrown);

      var message = jqXHR.responseJSON.status ? jqXHR.responseJSON.status.info : 'Something unexpected occurred';

      if (textStatus === 'timeout') {
        message = 'Cannot contact the server';
      } else if (jqXHR.status >= 500) {
        message = 'Internal server error';
      }

      createBotMessage(message, 'error', -1, jqXHR);
    }
  });
}

function printLog(entry) {
  document.getElementById('MSG_JSON').textContent = JSON.stringify(entry, null, 2);
  Prism.highlightAll();
}

function enableChat() {
  CHAT_MESSAGES.style.cursor = 'auto';
  CHAT_INPUT.disabled = false;
  CHAT_INPUT.value = '';
  CHAT_INPUT.focus();
}

function disableChat() {
  CHAT_MESSAGES.style.cursor = 'progress';
  CHAT_INPUT.disabled = true;
  CHAT_INPUT.value = '';
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
  VOICE_LIST.innerHTML = speechSynthesis.getVoices().map((voice, index) => `
    <label class=dropdown-item title="${ voice.name } (${ voice.lang })">
      <input type=radio name=voices ${ voice.default ? 'checked' : '' } value=${ index }> ${ voice.name } (${ voice.lang })
    </label>
  `).join('');
}
