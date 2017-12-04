function sanitize(string) {
  return string.replace(/[\x26\x0A\<>'"]/g, char => `&#${ char.charCodeAt(0) };`)
}

if (typeof module !== 'undefined') {
  // used for tests
  module.exports = {
    sanitize: sanitize
  }
}
