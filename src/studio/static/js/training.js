const statusFetcher = setInterval(pollStatus, 2000)
const trainingStatus = document.getElementById('trainingStatus')

function pollStatus() {
  fetch(`/proxy/ai/${ AI_ID }`, {
    credentials: 'same-origin'
  })
    .then(response => response.json())
    .then(ai => {
      console.debug(ai);
      trainingStatus.value = Math.ceil(ai.training.progress)
      trainingStatus.dataset.label = ai.training.status
      if (ai.training.status === 'ai_training_complete') {
        trainingStatus.parentElement.parentElement.classList.add('alert-success')
        trainingStatus.parentElement.parentElement.classList.remove('alert-info')
        clearInterval(statusFetcher)
      }
    })
    .catch(error => {
      console.error(error);
    })
}
