import os
import base64
import random
import string
import uuid
from datetime import datetime
from PyQt5.QtWidgets import (QGroupBox, QComboBox, QWidget, QPushButton, QTextEdit,
                             QVBoxLayout, QMessageBox, QFileDialog, QHBoxLayout,
                             QFrame, QListWidget, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QProgressBar, QRadioButton, QScrollArea,
                             QGridLayout, QLineEdit, QCheckBox, QSpinBox, QTabWidget,
                             QPlainTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
from docx import Document
import msoffcrypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from PIL import Image
import stepic
from pydub import AudioSegment
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TextFrame
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
import numpy as np
import wave


class StegoTool:
    def __init__(self):
        self.key_bytes = None  # ต้องกำหนดก่อนใช้ encrypt/decrypt

    def gen_secure_key(self, length=32):
        """Generate cryptographically secure key"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    def encrypt(self, message: str) -> str:
        """เข้ารหัสด้วย AES-256-CBC และส่งกลับเป็น Base64"""
        if not self.key_bytes or len(self.key_bytes) != 32:
            raise ValueError("key_bytes must be 32 bytes for AES-256")
        iv = get_random_bytes(16)
        cipher = AES.new(self.key_bytes, AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        encrypted_b64 = base64.b64encode(iv + ct_bytes).decode('utf-8')
        return encrypted_b64

    def decrypt(self, encrypted_b64: str) -> str:
        """ถอดรหัสด้วย AES-256-CBC จาก Base64"""
        try:
            encrypted_data = base64.b64decode(encrypted_b64)
            iv = encrypted_data[:16]
            ct = encrypted_data[16:]
            cipher = AES.new(self.key_bytes, AES.MODE_CBC, iv)
            pt_bytes = unpad(cipher.decrypt(ct), AES.block_size)
            return pt_bytes.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")

    def str_to_bin(self, text):
        """แปลง string เป็น binary string"""
        try:
            return ''.join(format(b, '08b') for b in text.encode('utf-8'))
        except:
            return ""

    def bin_to_str(self, bin_str):
        """แปลง binary string เป็น string"""
        try:
            if bin_str.endswith("00000000"):
                bin_str = bin_str[:-8]
            if len(bin_str) == 0:
                return ""
            n = (len(bin_str) + 7) // 8
            byte_val = int(bin_str, 2).to_bytes(n, 'big')
            return byte_val.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"[bin_to_str error] {e}")
            return ""

    def hide_lsb_image(self, img_path, msg, out_path):
        """ซ่อนข้อมูลในภาพด้วย LSB"""
        try:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert("RGBA")
                    alpha = img.split()[-1]
                    bg.paste(img.convert('RGB'), mask=alpha)
                    img = bg
                else:
                    img = img.convert('RGB')
            arr = np.array(img)
            bin_msg = self.str_to_bin(msg) + '00000000'
            h, w, c = arr.shape
            if len(bin_msg) > h * w * c:
                raise ValueError("ข้อความยาวเกินไปสำหรับภาพนี้")

            idx = 0
            for i in range(h):
                for j in range(w):
                    for k in range(c):
                        if idx < len(bin_msg):
                            arr[i, j, k] = (arr[i, j, k] & 0xFE) | int(bin_msg[idx])
                            idx += 1
            Image.fromarray(arr).save(out_path, 'PNG')
            return True
        except Exception as e:
            print(f"[ERROR] hide_lsb_image: {e}")
            return False

    def extract_lsb_image(self, img_path):
        """ดึงข้อมูลจากภาพด้วย LSB หยุดเมื่อเจอ 00000000"""
        try:
            img = Image.open(img_path).convert('RGB')
            arr = np.array(img)
            bin_data = ""
            for val in arr.flatten():
                bin_data += str(val & 1)
                if len(bin_data) % 8 == 0 and bin_data.endswith("00000000"):
                    try:
                        n = (len(bin_data) - 8) // 8
                        byte_val = int(bin_data[:-8], 2).to_bytes(n, 'big')
                        return byte_val.decode('utf-8', errors='replace')
                    except:
                        continue
            return self.bin_to_str(bin_data)
        except Exception as e:
            print(f"[ERROR] extract_lsb_image: {e}")
            return ""

    def hide_lsb_audio(self, audio_path, data, out_dir="audio_output"):
        """ซ่อนข้อมูลในไฟล์เสียงด้วย LSB"""
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
                sampwidth = params.sampwidth
                frames = af.readframes(af.getnframes())

            if sampwidth == 1:
                dtype = np.uint8
            elif sampwidth == 2:
                dtype = np.int16
            else:
                raise ValueError("รองรับเฉพาะ 8 หรือ 16 bit")

            audio_data = np.frombuffer(frames, dtype=dtype)
            bin_data = self.str_to_bin(data) + '00000000'

            if len(bin_data) > len(audio_data):
                raise ValueError("ข้อมูลยาวเกินไปสำหรับฝังในไฟล์เสียงนี้")

            mod_data = np.copy(audio_data)
            for i, bit in enumerate(bin_data):
                mod_data[i] = (mod_data[i] & ~1) | int(bit)

            if out_dir.lower().endswith(".wav"):
                out_path = out_dir
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            else:
                os.makedirs(out_dir, exist_ok=True)
                base_filename = os.path.splitext(os.path.basename(audio_path))[0]
                out_path = os.path.join(out_dir, f"{base_filename}_hidden.wav")

            with wave.open(out_path, 'wb') as wf:
                wf.setparams(params)
                wf.writeframes(mod_data.tobytes())

            return out_path
        finally:
            if temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)

    def extract_lsb_audio(self, audio_path):
        """ดึงข้อมูลจากไฟล์เสียงด้วย LSB"""
        try:
            if not os.path.exists(audio_path):
                return ""
            with wave.open(audio_path, 'rb') as af:
                params = af.getparams()
                sampwidth = params.sampwidth
                frames = af.readframes(af.getnframes())

            if sampwidth == 1:
                dtype = np.uint8
            elif sampwidth == 2:
                dtype = np.int16
            else:
                raise ValueError("รองรับเฉพาะ 8 หรือ 16 bit")

            audio_data = np.frombuffer(frames, dtype=dtype)
            bin_data = ""
            for b in audio_data:
                bin_data += str(b & 1)
                if len(bin_data) % 8 == 0 and bin_data.endswith("00000000"):
                    try:
                        n = (len(bin_data) - 8) // 8
                        byte_val = int(bin_data[:-8], 2).to_bytes(n, 'big')
                        return byte_val.decode('utf-8', errors='replace')
                    except:
                        continue
            return self.bin_to_str(bin_data)
        except Exception as e:
            print(f"[ERROR] extract_lsb_audio: {e}")
            return ""

    def hide_data_in_image(self, image_path, data, output_path):
        return self.hide_lsb_image(image_path, data, output_path)

    def hide_data_in_audio(self, audio_path, data, output_path):
        return self.hide_lsb_audio(audio_path, data, output_path)

    def hide_data_in_video(self, video_path, data, output_path):
        """ซ่อนข้อมูลใน metadata ของไฟล์วิดีโอ (MP4)"""
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"ไม่พบไฟล์วิดีโอ: {video_path}")

            import shutil
            shutil.copy(video_path, output_path)

            video = MP4(output_path)
            key = '----:com.stego.secret'
            data_bytes = data.encode('utf-8')
            video[key] = [data_bytes]
            video.save()

            print(f"🎥 ซ่อนข้อมูลในวิดีโอ (metadata) ที่: {output_path}")
            return output_path, None, True  # คืนค่า 3 ตัว

        except Exception as e:
            print(f"[ERROR] hide_data_in_video: {e}")
            return None, str(e), False

    def extract_lsb_video(self, video_path):
        """ดึงข้อมูลจาก metadata ของไฟล์วิดีโอ (MP4)"""
        try:
            if not os.path.exists(video_path):
                return ""
            video = MP4(video_path)
            key = '----:com.stego.secret'
            if key in video:
                data_bytes = video[key][0]
                return data_bytes.decode('utf-8')
            return ""
        except Exception as e:
            print(f"[ERROR] extract_lsb_video: {e}")
            return ""

    def extract_hidden_data(self, path):
        """ดึงข้อมูลจากสื่อต่าง ๆ ตามประเภทไฟล์"""
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg']:
            return self.extract_lsb_image(path)
        elif ext in ['.wav']:
            return self.extract_lsb_audio(path)
        elif ext in ['.mp4', '.mov']:
            return self.extract_lsb_video(path)
        else:
            return ""


# === ใช้งานจริง ===
tool = StegoTool()

# --- ข้อความลับ
message = "🔐 ทดสอบการเข้ารหัสและซ่อนแบบ LSB ทั้งภาพ เสียง วิดีโอ"
password = "batmanrocks"

# --- สร้างกุญแจและกำหนดให้ tool
key_str = tool.gen_secure_key()
tool.key_bytes = key_str.encode('utf-8')  # 🔑 สำคัญมาก
print(f"🔑 Key: {key_str}")

# --- เข้ารหัส
try:
    encrypted_b64 = tool.encrypt(message)
    print(f"🔒 Encrypted (Base64): {encrypted_b64}")
except Exception as e:
    print(f"❌ เข้ารหัสล้มเหลว: {e}")
    exit()

# --- แบ่งข้อมูล
total_len = len(encrypted_b64)
image_len = int(total_len * 0.2)
audio_len = int(total_len * 0.3)
video_len = total_len - image_len - audio_len

image_data = encrypted_b64[:image_len]
audio_data = encrypted_b64[image_len:image_len + audio_len]
video_data = encrypted_b64[image_len + audio_len:]

# --- Paths
img_in = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\example2.jpg"
aud_in = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\wave.wav"
vid_in = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\mm.mp4"
img_out = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\output_lsb_image.png"
aud_out = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\output_hidden_audio.wav"
vid_out = r"C:\Users\65011\Desktop\Segano\work00002\output_files\test\output_video_metadata.mp4"

# --- ซ่อนข้อมูล
success_img = tool.hide_data_in_image(img_in, image_data, img_out)
success_aud = tool.hide_data_in_audio(aud_in, audio_data, aud_out)
# เดิม: success_vid = tool.hide_data_in_video(...)
# แก้เป็น:
output_path_vid, error_vid, success_vid = tool.hide_data_in_video(vid_in, video_data, vid_out)

if not (success_img and success_aud and success_vid):
    print("⚠️ การซ่อนข้อมูลล้มเหลวบางส่วน")
else:
    print("✅ ข้อมูลถูกเข้ารหัสและซ่อนไว้ในไฟล์เรียบร้อยแล้ว")

# --- ทำความสะอาดข้อมูลที่ดึงกลับมา
def clean_b64(s):
    import re
    return re.sub(r'[^A-Za-z0-9+/=]', '', s) if s else ""

data1 = clean_b64(tool.extract_hidden_data(img_out))
data2 = clean_b64(tool.extract_hidden_data(aud_out))
data3 = clean_b64(tool.extract_hidden_data(vid_out))

recombined_b64 = data1 + data2 + data3

print(f"🔍 ความยาวรวม: {len(recombined_b64)} / ต้นฉบับ: {len(encrypted_b64)}")

# เติม = ถ้าจำเป็น
if len(recombined_b64) % 4 != 0:
    recombined_b64 += '=' * (4 - len(recombined_b64) % 4)

# --- ตรวจสอบ Base64 ก่อนถอดรหัส
try:
    base64.b64decode(recombined_b64)
except Exception as e:
    print(f"❌ Base64 ไม่ถูกต้อง: {e}")
    exit()

# --- ถอดรหัส
try:
    decrypted = tool.decrypt(recombined_b64)
    print("🔓 ข้อความที่ถอดรหัสได้:", decrypted)
except Exception as e:
    print(f"❌ ถอดรหัสล้มเหลว: {e}")
    print(f"ข้อมูลรวม (clean): {repr(recombined_b64)}")