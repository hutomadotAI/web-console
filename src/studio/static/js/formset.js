$(document)
  .on('change', '.form-formset .delete', function () {
    // Don’t validate removed formsets

    if (this.checked) {
      if ($(this).parents('.form-formset-group').length && !$(this).parent().hasClass('nested')) {
        $(this).parents('.form-formset-group').find('[required]').removeAttr('required');
        $(this).parents('.form-formset-group').addClass('removed');
      } else {
        $(this).parent().find('[required]').removeAttr('required').addClass('was-required');
      }
    } else {
      if ($(this).parents('.form-formset-group').length && !$(this).parent().hasClass('nested')) {
        $(this).parents('.form-formset-group').find('.was-required').attr('required');
        $(this).parents('.form-formset-group').removeClass('removed');
      } else {
        $(this).parent().find('.was-required').attr('required');
      }
    }

  });

$(document).on('click', '.formset-button', function () {
  // Get elements
  const FORMSET = document.getElementById(`${ this.dataset.formset }_FORMSET`);
  const TEMPLATE = document.getElementById(`${ this.dataset.formset }_TEMPLATE`);
  const TOTAL = document.getElementById(`id_${ this.dataset.formset }-TOTAL_FORMS`);

  // creat new form html
  var form = document.createElement('div');

  // replace prefix with entities forms counter
  var template = TEMPLATE.innerHTML.replace( /__prefix__-__prefix__/g, '__prefix__-0');
  template = template.replace( /__prefix__/g, TOTAL.value);

  form.innerHTML = template;


  // Append new form to the formset
  var newForm = FORMSET.appendChild(form.firstElementChild);

  // Enable tokenfields
  $(newForm).find('[data-tokenfield]').tokenfield(TOKENFIELD_OPTIONS);

  // Update forms counter
  TOTAL.value++;
});

