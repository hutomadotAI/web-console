$(document)
  .on('submit', '[method=delete]', function (event) {
    event.preventDefault()
    var id = $(this).data('id')

    fetch(this.action, {
      credentials: 'same-origin',
      method: 'delete',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      }
    })
      .then(response => response.json())
      .then(response => {
        // Determined status
        var success = (response.status.code == 200)
        var level = success ? 'success' : 'danger'

        // Give user a feedback
        $('.elements').before(messageAdd(level, response.status.info))

        // Remove the element
        if (success) {
          $('.elements').find(`.element-${ id }`).remove()
        }

        // Hide the parents modal
        $(this).parents('.modal').modal('hide')
      })
      .catch(error => {
        console.error(error)
      })
    console.debug(this)
  })

$('#delete_element').on('show.bs.modal', function (event) {
  var action = $(event.relatedTarget).data('action')
  var id = $(event.relatedTarget).data('id')

  $(this).find('#delete_element_form')
    .attr('action', action)
    .data('id', id)
  $(this).find('.element-id').text(id)
})
