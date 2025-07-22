import base64
import hashlib
from Crypto.Cipher import AES, Blowfish, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet



def aes_encrypt(data, key):
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return "<font color='blue'>"+ base64.b64encode(iv + encrypted_data).decode('utf-8')

def rsa_encrypt(message, public_key):
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted = cipher.encrypt(message.encode())
    return "<font color='purple'>" + base64.b64encode(encrypted).decode('utf-8')

def rsa_decrypt(encrypted_message, private_key):
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
    return decrypted.decode('utf-8')

def blowfish_encrypt(data, key):
    cipher = Blowfish.new(key.encode(), Blowfish.MODE_ECB)
    padded_data = pad(data.encode(), Blowfish.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return "<font color='orange'>" + base64.b64encode(encrypted_data).decode('utf-8')

def fernet_encrypt(message):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(message.encode('utf-8'))
    return "<font color='brown'>" + base64.b64encode(encrypted).decode('utf-8'), key.decode()


