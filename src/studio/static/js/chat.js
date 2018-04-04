const LOGS = document.getElementById('LOGS');

const CHAT_ID_KEY = `${AI.id}_chat_id`;
const HISTORY_KEY = `${AI.id}_history`;

const HISTORY = JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || [];

var showJsonWindow = true; // json window showed for default
var speechResponse = false;
var recording = false;

var waiting = false;

// Attach listeners
document.getElementById('action.logs:toggle').addEventListener('click', toggleLogs);
document.getElementById('action.logs:wrap').addEventListener('click', wrapLines);

document.getElementById('action.history:clear').addEventListener('click', clearHistory);

// Enable features
if ('speechSynthesis' in window) {
  document.getElementById('action.speech:toggle').addEventListener('click', toggleSpeech);
} else {
  document.getElementById('action.speech:toggle').classList.toggle('disabled');
}

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  document.getElementById('action.speech:dictate').addEventListener('click', dictateSpeech);
} else {
  document.getElementById('action.speech:dictate').disabled = true;
  document.getElementById('action.speech:dictate').setAttribute('title', 'Your browser dosn’t support it');
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
  document.getElementById('messages').innerHTML = '';
}

/**
 * Load chat history
 *
 * @return {undefined}
 */
function loadHistory() {
  HISTORY.forEach(entry => createMessage(...entry));
  $('#messages').scrollTop($('#messages').prop('scrollHeight'));
}


function createMessage(creator, data) {
  switch(creator) {
  case 'BOT':
    createBotMessage(...data, false);
    break;
  case 'USER':
    createUserMessage(...data, false);
    break;
  }
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
    recording = startDictation(function (results) {
      waiting = true;
      var message = results.error || results[0][0].transcript;
      var level = results.error ? 'error' : 'normal';
      createUserMessage(USER.name, message, Date.now(), level);
      if (level === 'normal') {
        requestAnswerAI(message);
      }
      recording = false;
      button.classList.remove('record');
    });
  }
}

function keyboardChat(e) {
  if (e.keyCode === 13 && document.getElementById('message').value) {
    createNodeChat();
  }
}

function createNodeChat() {
  var message = $('#message').val().trim();

  if (message && !waiting) {
    waiting = true;
    disableChat();
    createUserMessage(USER.name, message, Date.now(), 'normal');
    requestAnswerAI(message);
  }
}

function getPrintableLocalDateTime(timestamp) {
  return new Date(timestamp).toString().split(' ').slice(0, 5).join(' ');
}

function cutText(phrase) {
  const maximumTextLenght = 150; // characters
  if (phrase.length > maximumTextLenght) {
    var chunk = phrase.substr(0, maximumTextLenght);
    return chunk;
  }
  return phrase;
}

function createUserMessage(name, message, timestamp, level, save=true) {
  if (save) {
    updateHistory('USER', [...arguments]);
  }

  var height = parseInt($('#messages').scrollTop());

  if (save) {
    var interval = window.setInterval(scroll, 10);
  }

  var comment = document.createElement('div');
  comment.className = 'direct-chat-msg user';

  comment.innerHTML = `
    <div class="direct-chat-info clearfix">
      <span class="direct-chat-timestamp">${ getPrintableLocalDateTime(timestamp) }</span>
      <span class="direct-chat-name" style="color:gray;">${ name }</span>
    </div>
    <div class="direct-chat-text chat-${ level }">
      ${ cleanChat(message) }
    </div>
  `;

  document.getElementById('messages').appendChild(comment);

  function scroll() {
    if (parseInt($('#messages')[0].scrollHeight) < parseInt(height)) {
      clearInterval(interval);
    }
    height = parseInt(height) + 5;
    $('#messages').scrollTop(height);
  }

}

function createBotMessage(name, message, timestamp, level, score, log, save=true) {
  if (save) {
    updateHistory('BOT', [...arguments]);
  }

  if (save) {
    var interval = window.setInterval(scroll, 10);
  }

  var height = parseInt($('#messages').scrollTop());

  var score = score !== -1 ? `<span class=" pull-left text-sm text-white">score: ${ score }</span>` : '';

  var comment = document.createElement('div');
  comment.className = 'direct-chat-msg bot';
  comment.innerHTML = `
    <div class="direct-chat-info clearfix">
      <span class="direct-chat-name" style="color:gray;">${ name }</span>
      <span class="direct-chat-timestamp">${ getPrintableLocalDateTime(timestamp) }</span>
    </div>
    <div class="direct-chat-text chat-${ level }">
      ${ sanitize(message) }
    </div>
    ${ score }
  `;

  comment.addEventListener('click', () => printLog(log));

  document.getElementById('messages').appendChild(comment);

  if (speechResponse) {
    speak(cutText(message), enableChat);
  } else {
    enableChat();
  }

  function scroll() {
    if (parseInt($('#messages')[0].scrollHeight) < parseInt(height)) {
      clearInterval(interval);
    }
    height = parseInt(height) + 5
    $('#messages').scrollTop(height)
  }
}

function printLog(entry) {
  document.getElementById('MSG_JSON').textContent = JSON.stringify(entry, null, 2);
  Prism.highlightAll();
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
          level = 'error';
          message = 'No chat id returned';
        }
      }

      createBotMessage(AI.name, message, Date.now(), level, score, response);
    },
    error: function (jqXHR, textStatus, errorThrown) {

      console.debug(jqXHR, textStatus, errorThrown);

      if (textStatus === 'timeout') {
        createBotMessage(AI.name, 'Cannot contact the server', Date.now(), 'error', -1, jqXHR);
      } else if (jqXHR.status >= 500) {
        createBotMessage(AI.name, 'Internal server error', Date.now(), 'error', -1, jqXHR);
      } else {
        var message = jqXHR.responseJSON.status ? jqXHR.responseJSON.status.info : 'Something unexpected occurred';
        createBotMessage(AI.name, message, Date.now(), 'error', -1, jqXHR);
      }

    }
  });
}

function enableChat() {
  document.getElementById('messages').style.cursor = 'auto';
  document.getElementById('message').disabled = false;
  document.getElementById('message').value = '';
  document.getElementById('message').focus();
}

function disableChat() {
  document.getElementById('messages').style.cursor = 'progress';
  document.getElementById('message').disabled = true;
  document.getElementById('message').value = '';
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

function cleanChat(msg) {
  msg = msg.replace('&', '&#38');
  msg = msg.replace('/', '&#47');
  return msg.replace('<', '&#60').replace('\>', '&#62;').trim();
}
