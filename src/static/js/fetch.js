/**
 * Check response status and reject Promise on error
 * @param  {Promise} response incoming response
 *
 * @return {Promise} resolved or rejected response
 */
function resolveStatus(response) {
  return response.ok ? response : Promise.reject(response);
}

/**
 * Process response errors, reloads the page if not authenticated
 * @param  {Promise} response incoming response
 *
 * @throws {message/response} in every case
 */
function handleErrors(response) {
  if (response.status == 401) {
    window.location.reload(true);
  }

  throw({ message: response.statusText, response: response });
}
