document.getElementById('regenerate_webhook').addEventListener('submit', getSecret)

function getSecret(event) {
  event.preventDefault()

  fetch(this.getAttribute('action'), {
    credentials: 'same-origin',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')
    },
    body: new FormData(this)
  })
    .then(response => response.json())
    .then(webhookSecret => {
      console.debug(webhookSecret);
      document.getElementById('webhook_signing_secret').value = webhookSecret.status.info
      $('#regenHmacSecret').modal('hide')
    })
    .catch(error => {
      console.error(error)
    })
}
