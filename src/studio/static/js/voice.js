/**
 * Use SpeechSynthesis to read the message
 *
 * @param  {string} text Text to be read
 *
 * @return {undefined}
 */
function speak(text, callback, voiceId) {
  console.debug('speak');

  if ('speechSynthesis' in window) {
    var voices = window.speechSynthesis.getVoices();
    var utterance = new SpeechSynthesisUtterance();
    utterance.volume = 1;
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.voice = voices[voiceId];
    utterance.text = text;
    utterance.addEventListener('start', function () {
      console.debug('Synthesis started');
    });
    utterance.addEventListener('end', function () {
      console.debug('Synthesis ended');
      callback();
    });

    speechSynthesis.speak(utterance);
  }
}

/**
 * Use SpeechRecognition to record users input
 *
 * @return {SpeechRecognition}          Started recognition
 */
function startDictation(callback) {
  if ('webkitSpeechRecognition' in window) {
    var recognition = new webkitSpeechRecognition();
    var message = '';
    var level = 'normal';
    console.debug('Start Dictation');

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.addEventListener('result',  function (event) {
      console.debug('recognition resulted');
      recognition.stop();
      message = event.results[0][0].transcript;
    });

    recognition.addEventListener('error', function (error) {
      console.debug('recognition error');
      recognition.stop();
      message = error.error;
      level = 'error'
    });

    recognition.addEventListener('end', function () {
      console.debug('recognition end');
      callback(message, level);
    });

    recognition.start();

    return recognition;
  }
}

/**
 * Stops Speech Recognition
 *
 * @param  {SpeechRecognition} recognition Recognition to be stopped
 *
 * @return {boolean}           recording status
 */
function stopDictation(recognition) {
  recognition.stop();
  console.debug('recording stopped');
  return false;
}
