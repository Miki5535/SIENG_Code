import base64
import os
import uuid
import random
import string
import wave
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PIL import Image
from pydub import AudioSegment


def str_to_bin(text):
    try:
        return ''.join(format(b, '08b') for b in text.encode('utf-8'))
    except:
        return ""

def bin_to_str(bin_str):
    try:
        if bin_str.endswith("00000000"):
            bin_str = bin_str[:-8]
        n = len(bin_str)
        byte_data = int(bin_str, 2).to_bytes((n + 7) // 8, 'big')
        return byte_data.decode('utf-8')
    except:
        return ""

def gen_key(length=32):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def encrypt_aes(text, key_str=None):
    if not key_str:
        key_str = gen_key()
    print("\n----------------------------\n")
    print(key_str)
    print("\n----------------------------\n")
    key = key_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    iv_b64 = base64.b64encode(cipher.iv).decode()
    ct_b64 = base64.b64encode(ct).decode()
    encrypted_b64 = base64.b64encode(cipher.iv + ct).decode()
    return iv_b64, ct_b64, key_str, encrypted_b64


def decrypt_aes(iv_b64, ct_b64, key_str):
    try:
        key = key_str.encode('utf-8')
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except:
        return None

def split_msg(msg, parts=2):
    length = len(msg)
    return [msg[i*length//parts : (i+1)*length//parts] for i in range(parts)]

def hide_lsb_image(img_path, msg, out_path):
    try:
        img = Image.open(img_path)
        print(f"[DEBUG] Original mode: {img.mode}")

        # แปลงเป็น RGB อย่างปลอดภัย
        if img.mode != 'RGB':
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # สร้างพื้นหลังสีขาว
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert("RGBA")
                alpha = img.split()[-1]
                bg.paste(img.convert('RGB'), mask=alpha)
                img = bg
            else:
                img = img.convert('RGB')
        else:
            img = img.convert('RGB')

        arr = np.array(img)
        bin_msg = str_to_bin(msg) + '00000000'
        h, w, c = arr.shape

        if len(bin_msg) > h * w * c:
            raise ValueError("Message too long for image")

        idx = 0
        for i in range(h):
            for j in range(w):
                for k in range(c):
                    if idx < len(bin_msg):
                        arr[i, j, k] = (arr[i, j, k] & 0xFE) | int(bin_msg[idx])
                        idx += 1

        # บันทึกเป็น PNG (lossless)
        Image.fromarray(arr).save(out_path, 'PNG')
        print(f"[INFO] Saved to {out_path}")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def hide_lsb_audio(audio_path, data, out_dir="audio_output"):
    if not os.path.exists(audio_path) or not data.strip():
        return None
    ext = os.path.splitext(audio_path)[1].lower()
    temp_wav = None
    use_path = audio_path
    if ext != ".wav":
        audio = AudioSegment.from_file(audio_path)
        temp_wav = f"temp_{uuid.uuid4().hex}.wav"
        audio.export(temp_wav, format="wav")
        use_path = temp_wav
    try:
        with wave.open(use_path, 'rb') as af:
            params = af.getparams()
            frames = af.readframes(af.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.uint8)
        bin_data = str_to_bin(data) + '00000000'
        if len(bin_data) > len(audio_data):
            raise ValueError("Data too long for audio")
        mod_data = audio_data.copy()
        for i, b in enumerate(bin_data):
            mod_data[i] = (mod_data[i] & 0xFE) | int(b)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(audio_path))[0] + "_hidden.wav")
        with wave.open(out_path, 'wb') as of:
            of.setparams(params)
            of.writeframes(mod_data.tobytes())
        return out_path
    finally:
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)

def extract_lsb_image(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        arr = np.array(img)
        bin_data = ""
        for val in arr.flatten():
            bin_data += str(val & 1)
            if len(bin_data) % 8 == 0 and bin_data.endswith("00000000"):
                return bin_to_str(bin_data[:-8])
        return bin_to_str(bin_data)
    except:
        return ""

def extract_lsb_audio(audio_path):
    try:
        if not os.path.exists(audio_path):
            return ""
        with wave.open(audio_path, 'rb') as af:
            frames = af.readframes(af.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.uint8)
        bin_data = ""
        for b in audio_data:
            bin_data += str(b & 1)
            if len(bin_data) % 8 == 0 and bin_data.endswith("00000000"):
                return bin_to_str(bin_data[:-8])
        return bin_to_str(bin_data)
    except:
        return ""

class Stego:
    def hide(self, img_file, audio_file, msg, out_img="out.png", out_audio_dir="audio_output"):
        print("[INFO] Encrypting and hiding data...")
        iv, ct_b64, key_str, encrypted = encrypt_aes(msg)  # encrypted คือ base64(iv+ct)

        key_b64 = base64.b64encode(key_str.encode()).decode()
        key_hex = key_str.encode().hex()

        print(f"Key (Base64): {key_b64}\nKey (Hex): {key_hex}")
        print(f"Encrypted (Base64): {encrypted}")

        # แยก encrypted (ซึ่งเป็น string base64) ออกเป็น 2 ส่วน
        p1, p2 = split_msg(encrypted, 2)

        success_img = hide_lsb_image(img_file, p1, out_img)
        out_audio = hide_lsb_audio(audio_file, p2, out_audio_dir) if p2 else None

        return {
            "success": success_img and out_audio,
            "key_base64": key_b64,
            "key_hex": key_hex,
            "iv": iv,
            "encrypted": encrypted,
            "output_image": out_img,
            "output_audio": out_audio,
            "key_str": key_str
        }


    def extract(self, img_path, audio_path, key_b64):
        print("[INFO] Extracting and decrypting data...")
        p1 = extract_lsb_image(img_path)
        p2 = extract_lsb_audio(audio_path)
        if not p1 or not p2:
            print("[ERROR] Extraction failed.")
            return None
        encrypted = p1 + p2  # รวมเป็น encrypted base64 string
        try:
            encrypted_bytes = base64.b64decode(encrypted)
            iv = encrypted_bytes[:16]
            ct = encrypted_bytes[16:]
            key_str = base64.b64decode(key_b64).decode()
            key = key_str.encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            decrypted = pt.decode('utf-8')
            print(f"Decrypted: {decrypted}")
            return decrypted
        except Exception as e:
            print(f"[ERROR] Decryption failed: {e}")
            return None



