import base64
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def encrypt(plaintext: str, key: str) -> str:
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
    enc = cipher.encryptor()
    ciphertext = enc.update(padded) + enc.finalize()
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt(encrypted: str, key: str) -> str:
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    raw = base64.b64decode(encrypted)
    iv, ciphertext = raw[:16], raw[16:]
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(ciphertext) + dec.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")
