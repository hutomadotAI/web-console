/**
 * Use SpeechSynthesis to read the message
 *
 * @param  {string} text Text to be read
 *
 * @return {undefined}
 */
function speak(text, callback) {
  console.debug('speak')
  if ('speechSynthesis' in window) {
    var utterance = new SpeechSynthesisUtterance()
    utterance.volume = 1
    utterance.rate = 1
    utterance.pitch = 1
    utterance.text = text
    utterance.addEventListener('start', function () {
      console.debug('Synthesis started')
    })
    utterance.addEventListener('end', function () {
      console.debug('Synthesis ended')
      callback()
    })

    speechSynthesis.speak(utterance)
  }
}

/**
 * Use SpeechRecognition to record users input
 *
 * @return {SpeechRecognition}          Started recognition
 */
function startDictation(callback) {
  if ('webkitSpeechRecognition' in window) {
    var recognition = new webkitSpeechRecognition()
    var results = false;
    console.debug('Start Dictation')

    recognition.continuous = false
    recognition.interimResults = false
    recognition.addEventListener('result',  function (event) {
      console.debug('recognition resulted')
      recognition.stop()
      results = event.results
    })
    recognition.addEventListener('error', function (error) {
      console.debug('recognition error')
      recognition.stop()
      results = error
    })

    recognition.addEventListener('end', function (event) {
      console.debug('recognition end')
      callback(results || { error: 'Recognition error' })
    })

    recognition.start()

    return recognition
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
  recognition.stop()
  console.debug('recording stopped')
  return false
}
