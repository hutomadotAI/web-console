const statusFetcher = setInterval(pollStatus, 2000)
const trainingStatus = document.getElementById('trainingStatus')
const traningStatusText = document.getElementById('traningStatusText')

function pollStatus() {
  fetch(`/proxy/ai/${ AI.id }`, {
    credentials: 'same-origin'
  })
    .then(response => response.json())
    .then(ai => {
      console.debug(ai)
      trainingStatus.value = Math.ceil(ai.training.progress)
      traningStatusText.innerText = `${ ai.training.progress } % ${ ai.training.progress >= 25 && ai.training.progress < 100 ? traningStatusText.dataset.usable : '' }`
      if (ai.training.status === 'completed') {
        trainingStatus.parentElement.parentElement.classList.add('alert-success')
        trainingStatus.parentElement.parentElement.classList.remove('alert-info')
        clearInterval(statusFetcher)
      }
    })
    .catch(error => {
      console.error(error)
    })
}
