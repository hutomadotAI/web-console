$(document).ready(function(){
  const LINK = document.getElementById('DOWNLOAD_LOGS_ACTION');
  const LOGS_FORM = document.getElementById('LOGS_FORM');
  const LOGS_DOWNLOAD_TOKEN = 'logs_download_token';
  const OPTIONS = {
    todayHighlight: true,
    autoclose: true,
    format: 'yyyy-mm-dd',
    todayBtn: 'linked',
    endDate: new Date()
  };

  function changeDateHandler(selected) {
    var picker = $('#DATE_TO').data('datepicker');
    picker.setStartDate(new Date(selected.date.valueOf()));
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
  LOGS_FORM.addEventListener('submit', function submitHandler(event){
    event.preventDefault();
    var form = new FormData(event.target);
    var token = Date.now(); // Token is used for detecting dovnload completition in a single pageview
    LINK.href = [this.getAttribute('action'), token, form.get('from'), form.get('to')].join('/');
    LINK.click();

    // We use cookies to detect if download has eneded
    var timer = window.setInterval(function cookieChecker() {
      if (Cookies.get(LOGS_DOWNLOAD_TOKEN) == token) {
        window.clearInterval(timer);
        Cookies.remove(LOGS_DOWNLOAD_TOKEN);
        updateUI(event.target.id);
        console.debug('Logs has been downloaded');
      }
    }, 1000);
  });

});
