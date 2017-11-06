/**
 * Validate file type
 *
 * @param  {object} file   Current file to be validated
 * @param  {string} accept List of accepted types
 *
 * @return {boolean}        Is the file type accepted
 */
function validFileType(file, accept) {
  return accept.indexOf(file.type) != -1
}

/**
 * Validate file size
 *
 * @param  {object} file Current file to be validated
 * @param  {number} size Accepted filesize in bytes
 *
 * @return {boolean}      Is the file size valid
 */
function validFileSize(file, size) {
  return file.size <= size
}

document.querySelector('[type=file][data-type=image]')
  .addEventListener('change', function updateImageDisplay(event) {
  var files = event.target.files
  var message = ''

  if(files.length === 0) {
    message =messageAdd('error', 'No files currently selected for upload')
  } else {

    for(var i = 0; i < files.length; i++) {

      if(!validFileType(files[i], event.target.dataset.accept)) {
        message = messageAdd('error', 'Not a valid file type. Update your selection.')
      } else if (!validFileSize(files[i], event.target.dataset.size)) {
        message = messageAdd('error', `File size is more than ${ event.target.dataset.size / 1000 }kB, update your selection.`)
      } else {
        message = messageAdd('success', 'Image is ok')
        var image = document.createElement('img')
        image.src = window.URL.createObjectURL(files[i])

        event.target.parentElement.appendChild(image)
      }
      MESSAGES.appendChild(message)
    }
  }
})
