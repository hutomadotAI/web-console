$(document)
  .on('change', '.form-formset .delete', function (event) {
    // Don’t validate removed formsets
    $(this).parent().find('[required]').removeAttr('required')
  })
