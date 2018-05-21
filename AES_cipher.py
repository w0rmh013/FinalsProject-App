#!/usr/bin/python3
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class AESCipher(object):
    def __init__(self, key):
        self._bs = 32  # block size
        self._key = SHA256.new(key).digest()

    def _pad(self, s):
        return s + (self._bs - len(s) % self._bs) * chr(self._bs - len(s) % self._bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, data):
        """
        Encrypt data with AES CBC mode.

        :param data: plain data
        :return: encrypted data, encoded in base64
        """
        data = self._pad(data)
        iv = Random.new().read(AES.block_size)  # initialization vector
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(data)).decode()

    def decrypt(self, encrypted_data):
        """
        Decrypt data with AES cbc mode.

        :param encrypted_data: encrypted data
        :return: decrypted data
        """
        enc = base64.b64decode(encrypted_data)
        iv = enc[:AES.block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode()

    def __str__(self):
        return bytes.hex(self._key)
