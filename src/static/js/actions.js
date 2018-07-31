/**
 * Pushes send actions to GTM
 *
 * @param  {Event object} event dispatched click event
 *
 * @return {undefined}
 */
document.addEventListener('click', function handleClick(event) {
  if (event.target.getAttribute('action') === 'send') {

    if(dataLayer) {
      dataLayer.push({
        event: 'abstractEvent',
        eventCategory: 'action',
        eventAction: 'send',
        eventLabel: event.target.id,
        eventMetadata: {
          timestamp: Date.now()
        }
      });
    }
  }
});
