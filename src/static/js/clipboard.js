document.addEventListener('DOMContentLoaded', function(event) {
  // Enable copy to clipboard for all the triggerers containing targets
  const clipboard = new Clipboard('[data-clipboard-target]')

  function setTooltip(message, trigger) {
    $(trigger)
      .attr('data-original-title', message)
      .tooltip('show')
  }

  function hideTooltip(trigger) {
    setTimeout(function() {
      $(trigger)
        .tooltip('hide')
        .attr('data-original-title', 'Copy to clipboard')
    }, 2000)
  }

  clipboard.on('success', function(event) {
    setTooltip('Copied!', event.trigger)
    hideTooltip(event.trigger)
  })

});
