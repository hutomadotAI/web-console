const INTERVAL = 2000;
const AI_TRAINING = document.getElementById('AI_TRAINING');
const ICONS = {
  'empty': 'fa-circle-o',
  'training': 'fa-cog fa-spin'
};
const MESSAGE = document.querySelector('.messages .alert-success');

// Initial poll
setTimeout(pollStatus, INTERVAL);

/**
 * Updates HTML
 *
 * @param  {object} ai AI status
 *
 * @return {undefined}
 */
function updateUI(ai) {
  console.debug(ai);
  AI_TRAINING.className = `fa ${ ICONS[ai.training.status] || 'fa-circle' } circle training status-${ ai.training.status } pull-right`;
  AI_TRAINING.title = `Training status: ${ ai.training.status }`;
  $(AI_TRAINING).tooltip('update');

  if (TAB === 'training' && ai.training.status === 'completed' && MESSAGE) {
    MESSAGE.classList.add('hide');
  }
}

/**
 * Updates poll interval and fetches a new request
 *
 * @param  {object} response Incoming response
 *
 * @return {object}          Same response
 */
function updateInterval(response) {
  let interval = parseInt(localStorage.getItem('AI_status_interval'));

  if (response.ok) {
    interval = interval / 2 > INTERVAL ? interval / 2 : INTERVAL;
  } else {
    interval = interval * Math.ceil(Math.log(interval));
  }

  localStorage.setItem('AI_status_interval', interval);

  setTimeout(pollStatus, interval);

  return response;
}

/**
 * Fetches AI status
 *
 * @return {undefined}
 */
function pollStatus() {
  fetch(`/proxy/ai/${ AI.id }`, { credentials: 'same-origin' })
    .then(updateInterval)
    .then(resolveStatus)
    .catch(handleErrors)
    .then(response => response.json())
    .then(updateUI)
    .catch(error => console.error(error));
}
