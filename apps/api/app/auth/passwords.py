"""Argon2id password hashing + verification."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(stored_hash: str, plain: str) -> bool:
    try:
        _hasher.verify(stored_hash, plain)
    except VerifyMismatchError:
        return False
    return True


def needs_rehash(stored_hash: str) -> bool:
    return _hasher.check_needs_rehash(stored_hash)
