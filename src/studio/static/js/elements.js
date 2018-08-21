$('#delete_element').on('show.bs.modal', function setElementData(event) {
  var action = $(event.relatedTarget).data('action');
  var id = $(event.relatedTarget).data('id');

  $(this).find('#DELETE_ELEMENT_FORM')
    .attr('action', action)
    .data('id', id);
  $(this).find('.element-id').text(id);
});
