$('#delete_element').on('show.bs.modal', function (event) {
  var action = $(event.relatedTarget).data('action')
  var id = $(event.relatedTarget).data('id')

  $(this).find('#delete_element_form')
    .attr('action', action)
    .data('id', id)
  $(this).find('.element-id').text(id)
})
