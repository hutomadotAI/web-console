import hashlib

from django.conf import settings
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.encoding import force_bytes


class PBKDF2WrappedSHA256PasswordHasher(PBKDF2PasswordHasher):
    """
    Used to port old users passwords, after first login users password is updated
    to standard Django PBKDF2 SHA256.
    """
    algorithm = 'pbkdf2_wrapped_sha256'

    def encode_sha256_hash(self, sha256_hash, salt, iterations=None):
        return super(PBKDF2WrappedSHA256PasswordHasher, self).encode(sha256_hash, salt, iterations)

    def encode(self, password, salt, iterations=None):
        sha256_hash = hashlib.sha256(force_bytes(password + settings.LEGACY_SALT + salt)).hexdigest()
        encoded = self.encode_sha256_hash(sha256_hash, salt, iterations)
        return encoded
