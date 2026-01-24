import os
import base64
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import pyotp

# Konfiguracja Argon2
ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

# Stały klucz AES (32 bajty = 256 bitów)
AES_KEY = b"12345678901234567890123456789012"


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash: str, password: str) -> bool:
    try:
        return ph.verify(hash, password)
    except:
        return False


def encrypt_aes(plaintext: str) -> str:
    # Generowanie losowego IV (16 bajtów) dla każdego wpisu
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding PKCS7 (dopełnienie do bloku)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Zwracamy IV + Ciphertext zakodowane w Base64
    return base64.b64encode(iv + ciphertext).decode('utf-8')


def decrypt_aes(encrypted_b64: str) -> str:
    data = base64.b64decode(encrypted_b64)

    # Wyodrębnienie IV (pierwsze 16 bajtów)
    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Usunięcie paddingu
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(decrypted_padded) + unpadder.finalize()).decode('utf-8')


def generate_2fa_secret():
    return pyotp.random_base32()


def verify_2fa_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)