
$(document).ready(function () {
  loadFacebookAction('get');
});

var appid = "unknown";
var permissions = "unknown";
var custom_greeting = "";
var custom_get_started = "";

function htmlEncode(value) {
  return $('<div/>').text(value).html();
}

function saveFacebookCustomisations() {

  var page_greeting = $('#fb_page_greeting').val();
  var get_started_payload = $('#fb_get_started_payload').val();

  $("#fb-custom-save").text("Saving...");
  $.ajax({
    url: "./dynamic/integrations.facebook.customisations.php",
    type: "POST",
    contentType: "application/json", // send as JSON
    data: JSON.stringify({
      "page_greeting": page_greeting,
      "get_started_payload": get_started_payload
    }),
    complete: function () {
    },
    success: function () {
      $("#fb-custom-save").text("Save customisations");
      custom_greeting = page_greeting;
      custom_get_started = get_started_payload;
      showSaveIfThereAreChanges();
    },
    error: function (data) {
      $("#fb-custom-save").text("Save failed. Retry?");
      showSaveIfThereAreChanges();
    }
  });
}

function showSaveIfThereAreChanges() {
  if ((custom_greeting === $('#fb_page_greeting').val()) &&
    (custom_get_started === $('#fb_get_started_payload').val())) {
    $("#fb-custom-save").hide();
  } else {
    $("#fb-custom-save").show();
  }
}

function facebookConnect() {
  // https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
  var facebookRedir = htmlEncode(window.location.href.split('#')[0].split('?')[0]);
  document.cookie = "facebookRedir=" + facebookRedir + "; path=/";
  var fbLogin = "https://www.facebook.com/v2.9/dialog/oauth"
    + "?client_id=" + appid
    + "&scope=" + permissions
    + "&redirect_uri=" + facebookRedir;
  window.location.href = fbLogin;
}

function loadFacebookAction(action, id) {
  $("#facebookState").html("Loading...");
  if (action == null) {
    action = 'get';
  }
  if (id == null) {
    id = '0';
  }
  $("#facebookState").load("./integrations/facebook/" + action + '/' + id);
};


$("#facebookState").on("click", "#fb-disconnect", function () {
  loadFacebookAction("disconnect");
  return false;
});

$("#facebookState").on("click", ".fb-page-list", function () {
  var selectedPage = $(this).attr("id").substr(4);
  loadFacebookAction("page", selectedPage);
  return false;
});

$("#facebookState").on("click", "#fb-int-connect", function () {
  facebookConnect();
  return false;
});

$("#facebookState").on("click", "#fb-custom-save", function () {
  saveFacebookCustomisations()
  return false;
});

$("#facebookState").on("keyup", "#fb_page_greeting", function () {
  showSaveIfThereAreChanges();
});
$("#facebookState").on("keyup", "#fb_get_started_payload", function () {
  showSaveIfThereAreChanges();
});

