const STATUS_FETCHER = setInterval(pollStatus, 2000)
const AI_TRAINING = document.getElementById('AI_TRAINING')
const ICONS = {
  'empty': 'fa-circle-o',
  'training': 'fa-cog fa-spin'
}
const MESSAGE = document.querySelector('.messages .alert-success')

function pollStatus() {
  fetch(`/proxy/ai/${ AI.id }`, {
    credentials: 'same-origin'
  })
    .then(response => response.json())
    .then(ai => {
      console.debug(ai)
      AI_TRAINING.className = `fa ${ ICONS[ai.training.status] || 'fa-circle' } circle training status-${ ai.training.status } pull-right`
      AI_TRAINING.title = `Training status: ${ ai.training.status }`
      $(AI_TRAINING).tooltip('fixTitle')

      if (TAB === 'training' && ai.training.status === 'completed' && MESSAGE) {
        MESSAGE.classList.add('hide')
      }
    })
    .catch(error => {
      console.error(error)
    })
}
