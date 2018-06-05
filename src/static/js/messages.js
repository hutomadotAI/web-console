const MESSAGES = document.querySelector('.messages');

/**
 * Add a new message
 *
 * @param  {string} level    Message level in  order `error`, `warning`,
 *                           `success` or `info`
 * @param  {string} message Actual message to be presented
 *
 * @return {HTMLElement}     Message element
 */
function messageCreate(level, message) {
  return `<div class="alert alert-${ level }">${ message }</div>`;
}

function messageAdd(level, message) {
  MESSAGES.innerHTML += messageCreate(level, message);
}

function messageClear(level) {
  var selector = level ? `.messages .alert-${ level }` : '.messages .alert';
  document.querySelectorAll(selector).forEach(node => node.remove());
}
