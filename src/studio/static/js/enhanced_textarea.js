(function() {
  const TEXTAREA = document.getElementById('id_training_data');
  const FILE = document.getElementById('FILE');

  const MIMETYPE_BIANRY = {
    '89504E47': 'image/png',
    '47494638': 'image/gif',
    '25504446': 'application/pdf',
    'FFD8FFDB': 'image/jpeg',
    'FFD8FFE0': 'image/jpeg',
    '504B0304': 'application/zip'
  };

  /**
   * Check first 4 bites if they correspond to a binary file signature. More
   * info:
   * https://medium.com/the-everyday-developer/detect-file-mime-type-using-magic-numbers-and-javascript-16bc513d4e1e
   *
   * Update: Transform to normal array and add padding zeros
   *
   * @param  {[type]}  bytesArray   First bytes used to match the file signature
   * @return {Boolean}              Binary or not :)
   */
  function isBinary(bytesArray) {
    const HEX = Array.from(bytesArray).map(
      byte => byte.toString(16).padStart(2, '0')
    ).join('').toUpperCase();
    return HEX in MIMETYPE_BIANRY;
  }

  /**
   * If file is text not binary updates textarea and removes loading class.
   * Decodes UTF-8 buffer into string using TextDecoder.
   *
   * @param  {Event object} event
   */
  function loadHandler() {
    const UINT = new Uint8Array(this.result);

    if(isBinary(UINT.slice(0, 4))) {
      messageAdd('error', 'File type not supported, use a text file');
    } else {
      TEXTAREA.value += new TextDecoder().decode(UINT);
    }

    TEXTAREA.classList.remove('loading');

  }

  /**
   * If file is the right size process it's content
   *
   * @param  {File object} file
   */
  function processFile(file) {
    if (file.size > 1000000) {
      throw(`<b>${ file.name }</b>, File size is to big max. 1mb`);
    }

    let reader = new FileReader();
    reader.addEventListener('load', loadHandler);
    reader.readAsArrayBuffer(file);
  }

  /**
   * Clears textarea, adds loading class and proceeds uploaded or dropped files.
   *
   * @param  {Event object} event
   */
  function fileHandler(event) {

    // Prevent events, for Firefox
    event.stopPropagation();
    event.preventDefault();
    messageClear();

    TEXTAREA.value = '';

    let files = (event.dataTransfer || event.target).files;

    TEXTAREA.classList.add('loading');

    for (let file of files) {
      try {
        processFile(file);
      }
      catch(error) {
        messageAdd('error', error);
        console.error(error);

        TEXTAREA.classList.remove('loading');
      }
    }

  }

  /**
   * Triggers change event
   *
   * @param  {Event object} event
   */
  function syntheticChange() {
    TEXTAREA.dispatchEvent(new Event('change', { 'bubbles': true }));
  }

  function preventDefault(event) {
    event.stopPropagation();
    event.preventDefault();
  }

  // Prevent events, for Firefox
  TEXTAREA.addEventListener('drop', preventDefault);
  TEXTAREA.addEventListener('dragenter', preventDefault);
  TEXTAREA.addEventListener('dragover', preventDefault);

  TEXTAREA.addEventListener('drop', fileHandler);
  TEXTAREA.addEventListener('paste', syntheticChange);
  TEXTAREA.addEventListener('keyup', syntheticChange);
  TEXTAREA.addEventListener('drop', syntheticChange);
  FILE.addEventListener('change', syntheticChange);
  FILE.addEventListener('change', fileHandler);
})();
