$(document).on('change', '.form-formset .delete', function () {
  // Don’t validate removed formsets, use disable state to prevent it
  document.querySelectorAll(`[name^=${ this.dataset.prefix }]:not(.delete)`).forEach(
    node => node.disabled = this.checked
  );

  // Show removed for the nested formset group
  if (document.getElementById(this.dataset.prefix)) {
    document.getElementById(this.dataset.prefix).classList.toggle('removed');
  }
});

$(document).on('click', '.formset-button', function () {
  // Get elements
  const FORMSET = document.getElementById(`${ this.dataset.formset }_FORMSET`);
  const TEMPLATE = document.getElementById(`${ this.dataset.formset }_TEMPLATE`);
  const TOTAL = document.getElementById(`id_${ this.dataset.formset }-TOTAL_FORMS`);

  // Create new form html
  var form = document.createElement('div');

  // Prepare nested formsets prefixes and update current counter
  var template = TEMPLATE.innerHTML.replace( /__prefix__-__prefix__/ig, '__prefix__-__nested-prefix__');
  template = template.replace( /__prefix__/ig, TOTAL.value);
  template = template.replace( /__nested-prefix__/ig, '__prefix__');
  form.innerHTML = template;

  // Append new form to the formset
  var newForm = FORMSET.appendChild(form.firstElementChild);

  // Enable tokenfields
  $(newForm).find('[data-tokenfield]').tokenfield(TOKENFIELD_OPTIONS);

  // Update forms counter
  TOTAL.value++;
});

