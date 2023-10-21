"""The :mod:`app.utils.security` module contains resuable utils for security operations for web APIs
"""
# Author: Christopher Dare

import base64
import hashlib


def verify_user_pbkdf2_sha256_password(plain_password, hashed_password):
    """Verify user password using the PBKDF2 algorithm with SHA-256 as the underlying hash function for password hashing"""
    algo, iterations, salt, hsh = hashed_password.split("$")
    iterations = int(iterations)

    derived_key = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    stored_hsh = base64.b64decode(hsh.encode("utf-8"))

    return derived_key == stored_hsh
