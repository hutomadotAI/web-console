$(document).ready(function(){
  const LINK = document.getElementById('DOWNLOAD_LOGS_ACTION');
  const OPTIONS = {
    todayHighlight: true,
    autoclose: true,
    format: 'yyyy-mm-dd',
    todayBtn: 'linked',
    endDate: new Date()
  };

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
      button.disabled = false;
      button.classList.remove('loading');
    }
  }

  $('#DATE_TO').datepicker(OPTIONS);
  $('#DATE_FROM').datepicker(OPTIONS)
    .on('changeDate', changeDateHandler);

  // Fix updating loading state
  $('#LOGS_FORM').on('submit', function submitHandler(event){
    event.preventDefault();

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
        console.error(error);
      });
  });

});
