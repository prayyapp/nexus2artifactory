import os
import base64
import hashlib

class Password(object):
    @staticmethod
    def encrypt(pasw):
        key = os.urandom(16)
        return base64.b64encode(key + Password.crypto(key, pasw))

    @staticmethod
    def decrypt(enc64):
        enc = base64.b64decode(enc64)
        return Password.crypto(enc[:16], enc[16:])

    @staticmethod
    def crypto(key, pasw):
        out, j = [], 0
        digest = hashlib.sha1()
        digest.update(key + '|#4RC,\xe7-\xb1CEz[\x89\xe1C')
        key = digest.digest()
        S = range(256)
        for i in xrange(256):
            j = (j + S[i] + ord(key[i % len(key)])) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        for char in pasw:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
        return ''.join(out)
