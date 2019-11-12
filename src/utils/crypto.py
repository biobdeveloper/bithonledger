"""Cryptography module.

Encrypt and decrypt user's Bitcoin WIFs.
"""
import rncryptor
from base64 import b64encode, b64decode


def encrypt(wif, password):
    return b64encode(rncryptor.RNCryptor().encrypt(data=wif, password=password)).decode('utf-8')


def decrypt(enc_wif, password):
    return rncryptor.RNCryptor().decrypt(b64decode(enc_wif.encode('utf-8')), password=password)
