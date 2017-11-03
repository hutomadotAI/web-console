/**
 * Add a new message
 *
 * @param  {string} level    Message level in  order `error`, `warning`,
 *                           `success` or `info`
 * @param  {string} messsage Actual message to be presented
 *
 * @return {HTMLElement}     Message element
 */
function messageAdd (level, messsage) {
  var message = document.createElement('div')
  message.classList.add('alert', `alert-${ level }`)
  message.innerText = messsage

  return message
}
