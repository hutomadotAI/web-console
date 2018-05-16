document.getElementById('regenerate_webhook').addEventListener('submit', function getSecret(event) {
  event.preventDefault();
  const SUBMIT_BUTTONS = document.querySelectorAll(`[form=${event.target.id}]`);

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
      document.getElementById('WEBHOOK_SIGNING_SECRET').value = webhookSecret.status.info;
      for(let button of SUBMIT_BUTTONS) {
        button.disabled = false;
        button.classList.remove('loading');
      }
      $('#regenerate_webhook_secret').modal('hide');
    })
    .catch(error => {
      console.error(error);
    });
});
