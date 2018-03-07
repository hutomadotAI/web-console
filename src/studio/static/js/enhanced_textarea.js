const TEXTAREA = document.getElementById('id_training_data');
const FILE = document.getElementById('FILE');

function loadHandler(event) {
  TEXTAREA.classList.remove('loading');
  TEXTAREA.value += this.result;
}

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

TEXTAREA.addEventListener('drop', fileHandler);
FILE.addEventListener('change', fileHandler);
