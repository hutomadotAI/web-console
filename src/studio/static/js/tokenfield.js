const TOKENFIELD_OPTIONS = { createTokensOnBlur: true };

$(document)
  .ready(function() {
    // Initiate Tokenfields on window load event (we need to wait for jQuery)
    $('[data-tokenfield]').tokenfield(TOKENFIELD_OPTIONS);
  })
  .on('tokenfield:createdtoken', '[data-pattern],[data-max-length]', function (event) {
    // Delegate validation for fields containing `data-pattern` or
    // `data-maxlength`
    var valid = true;

    if (this.dataset.maxLength && event.attrs.value.length > this.dataset.maxLength) {
      valid = false;
    }

    if (this.dataset.pattern) {
      var re = new RegExp(this.dataset.pattern);
      valid = re.test(event.attrs.value);
    }

    if (!valid) {
      console.error(this);
      $(event.relatedTarget).addClass('invalid');
    }
  })
  .on('tokenfield:initialize', function () {
    // Synthetic changed triggers, need to bubble
    $(document).on('tokenfield:removedtoken tokenfield:createtoken', function (event) {
      event.target.dispatchEvent(new Event('tokenfield:changed', { 'bubbles': true }));
    });
  });

