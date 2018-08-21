$(document).on('click', '#FB_CONNECT_ACTION', function handleFacebookConnect() {
  // https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow

  var state = {
    next: 'studio:facebook_actions',
    action: 'connect',
    aiid: AI.id
  };

  window.location.href = 'https://www.facebook.com/v2.9/dialog/oauth'
    + '?client_id=' + APP_ID
    + '&scope=' + PERMISSIONS
    + '&redirect_uri=' + location.origin + '/oauth'
    + '&state=' + encodeURIComponent(JSON.stringify(state));
});


$(document).on('submit', '#FB_SETTINGS_FORM', function saveFacebookCustomisations(event) {

  event.preventDefault();

  var custom_greeting = '';
  var custom_get_started = '';
  var page_greeting = $('#fb_page_greeting').val();
  var get_started_payload = $('#fb_get_started_payload').val();

  $('[form=FB_SETTINGS_FORM]').text('Saving…');

  $.ajax({
    url: './integrations/facebook/customise',
    type: 'POST',
    contentType: 'application/json', // send as JSON
    beforeSend: function(xhr, settings) {
      xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
    },
    data: JSON.stringify({
      'page_greeting': page_greeting,
      'get_started_payload': get_started_payload
    }),
    complete: function () {
      $('[form=FB_SETTINGS_FORM]').removeClass('loading');
      $('[form=FB_SETTINGS_FORM]').removeAttr('disabled');
    },
    success: function () {
      $('[form=FB_SETTINGS_FORM]').text('Save customisations');
      custom_greeting = page_greeting;
      custom_get_started = get_started_payload;
    },
    error: function () {
      $('[form=FB_SETTINGS_FORM]').text('Save failed. Retry?');
    }
  });
});

$(document).on('click', '#REQUEST_INTEGRATION', function handleRequestIntegration() {
  if ('Intercom' in window) {
    Intercom('showNewMessage', this.dataset.message);
  }
});
