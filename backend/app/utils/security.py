"""The :mod:`app.utils.security` module contains resuable utils for security operations for web APIs
"""
# Author: Christopher Dare

import hashlib


def make_password(raw_password: str) -> str:
    assert raw_password
    hash = hashlib.md5(raw_password.encode('utf-8')).hexdigest()
    return hash

def check_password(hash: str, raw_password: str) -> bool:
    """Generates the hash for a raw_password and compares it."""
    generated_hash = make_password(raw_password)
    return hash == generated_hash