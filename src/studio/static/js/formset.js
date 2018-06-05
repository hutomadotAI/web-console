$(document)
  .on('change', '.form-formset .delete', function () {
    // Don’t validate removed formsets
    $(this).parent().find('[required]').removeAttr('required');
  });

$(document).on('click', '.formset-button', function () {
  // Get elements
  const FORMSET = document.getElementById(`${ this.dataset.formset }_FORMSET`);
  const TEMPLATE = document.getElementById(`${ this.dataset.formset }_TEMPLATE`);
  const TOTAL = document.getElementById(`id_${ this.dataset.formset }-TOTAL_FORMS`);

  // creat new form html
  var form = document.createElement('div');

  // replace prefix with entities forms counter
  form.innerHTML = TEMPLATE.innerHTML.replace( /__prefix__/g, TOTAL.value);

  // Append new form to the formset
  var newForm = FORMSET.appendChild(form.firstElementChild);

  // Enable tokenfields
  $(newForm).find('[data-tokenfield]').tokenfield(TOKENFIELD_OPTIONS);

  // Update forms counter
  TOTAL.value++;
});

