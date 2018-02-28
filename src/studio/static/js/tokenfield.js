const TOKENFIELD_OPTIONS = {
  createTokensOnBlur: true
}

$(document)
  .ready(function() {
    // Initiate Tokenfields on window load event (we need to wait for jQuery)
    $('[data-tokenfield]').tokenfield(TOKENFIELD_OPTIONS)
  })
  .on('tokenfield:createdtoken', '[data-pattern],[data-maxlength]', function (event) {
    // Delegate validation for fields containing `data-pattern` or
    // `data-maxlength`
    var valid = true

    if (this.dataset.maxlength && event.attrs.value.length > this.dataset.maxlength) {
        valid = false
    }

    if (this.dataset.pattern) {
      var re = new RegExp(this.dataset.pattern)
      valid = re.test(event.attrs.value)
    }

    if (!valid) {
      console.error(this)
      $(event.relatedTarget).addClass('invalid')
    }
  })
  .on('tokenfield:initialize', function (event) {
    // Synthetic changed triggers, need to bubble
    $(document).on('tokenfield:removedtoken tokenfield:createtoken', function (event) {
      event.target.dispatchEvent(new Event('tokenfield:changed', { 'bubbles': true }))
    })

  })

