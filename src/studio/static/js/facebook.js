$(document).on('click', '#fb-connect', function handleFacebookConnect() {
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


$(document).on('submit', '#FB_SETTINGS', function saveFacebookCustomisations(event) {

  event.preventDefault();

  var custom_greeting = '';
  var custom_get_started = '';
  var page_greeting = $('#fb_page_greeting').val();
  var get_started_payload = $('#fb_get_started_payload').val();

  $('[form=FB_SETTINGS]').text('Saving…');

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
      $('[form=FB_SETTINGS]').removeClass('loading');
      $('[form=FB_SETTINGS]').removeAttr('disabled');
    },
    success: function () {
      $('[form=FB_SETTINGS]').text('Save customisations');
      custom_greeting = page_greeting;
      custom_get_started = get_started_payload;
    },
    error: function () {
      $('[form=FB_SETTINGS]').text('Save failed. Retry?');
    }
  });
});
