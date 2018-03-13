(function() {
  const TEXTAREA = document.getElementById('id_training_data');
  const FILE = document.getElementById('FILE');

  /**
   * Updates textarea and removes loading class
   *
   * @param  {Event object} event
   */
  function loadHandler(event) {
    TEXTAREA.classList.remove('loading');
    TEXTAREA.value += this.result;
  }

  /**
   * Clears textarea, adds loading class and proceeds uploaded or dropped files.
   *
   * @param  {Event object} event
   */
  function fileHandler(event) {
    event.preventDefault();

    TEXTAREA.value = '';

    let files = (event.dataTransfer || event.target).files;

    TEXTAREA.classList.add('loading');

    for (file of files) {
      let reader = new FileReader();
      reader.addEventListener('load', loadHandler);
      reader.readAsText(file);
    }

  }

  /**
   * Triggers change event
   *
   * @param  {Event object} event
   */
  function syntheticChange(event) {
    TEXTAREA.dispatchEvent(new Event('change', { 'bubbles': true }))
  }

  TEXTAREA.addEventListener('drop', fileHandler);
  TEXTAREA.addEventListener('paste', syntheticChange);
  TEXTAREA.addEventListener('keyup', syntheticChange);
  TEXTAREA.addEventListener('drop', syntheticChange);
  FILE.addEventListener('change', syntheticChange);
  FILE.addEventListener('change', fileHandler);
})();
