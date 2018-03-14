$(document).ready(function(){
  const LINK = document.createElement('a');
  const OPTIONS = {
    todayHighlight: true,
    autoclose: true,
    format: 'yyyy-mm-dd',
    todayBtn: 'linked',
    todayHighlight: true,
    endDate: new Date()
  }

  LINK.download = `${ AI.id }_logs.csv`;

  function changeDateHandler(selected) {
    var picker = $('#chatlogsDateTo').data('datepicker');
    picker.setStartDate(new Date(selected.date.valueOf()));
  }

  function downloadData(data) {
    LINK.href = window.URL.createObjectURL(data);
    LINK.click();
  }

  function updateUI(id) {
    for(let button of document.querySelectorAll(`[form=${ id }]`)) {
      button.disabled = false
      button.classList.remove('loading')
    }
  }

  $('#chatlogsDateTo').datepicker(OPTIONS);
  $('#chatlogsDateFrom').datepicker(OPTIONS)
    .on('changeDate', changeDateHandler);

  // Fix updating loading state
  $('#LOGS_FORM').on('submit', function submitHandler(event){
    event.preventDefault()

    fetch(this.getAttribute('action'), {
      credentials: 'same-origin',
      method: 'post',
      headers: { 'X-CSRFToken': Cookies.get('csrftoken') },
      body: new FormData(this)
    })
      .then(response => response.blob())
      .then(downloadData)
      .then(() => updateUI(event.target.id))
      .catch(error => {
        console.error(error)
      })
  })

});
