import os
import json
import base64
import gzip
import hashlib
import zipfile
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from PIL import Image
import pydub
import moviepy.editor as mp
import gnupg
import docx

class WorkflowItem:
    def __init__(self, mode_id, mode_name, source_files, config):
        self.mode_id = mode_id
        self.mode_name = mode_name
        self.source_files = source_files
        self.config = config

    def __str__(self):
        return f"{self.mode_name}: {len(self.source_files)} ไฟล์"

class StegoFunctions:
    def validate_files(self, files, mode_id):
        required_files = {
            1: {'image': 1, 'audio': 1},
            2: {'video': 1},
            3: {'image': 1, 'audio': 1, 'video': 1},
            4: {'audio': 1, 'video': 1},
            5: {'image': 1, 'audio': 1, 'video': 1},
            6: {'image': 1, 'audio': 1, 'video': 1},
            7: {'image': 1, 'audio': 1, 'video': 1},
            8: {'image': 1, 'audio': 1, 'video': 1},
            9: {'image': 1, 'audio': 1, 'video': 1},
            10: {'zip': 1}
        }
        requirements = required_files.get(mode_id, {})
        file_counts = {'image': 0, 'audio': 0, 'video': 0, 'zip': 0}
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                file_counts['image'] += 1
            elif ext in ['.wav', '.mp3', '.flac', '.ogg']:
                file_counts['audio'] += 1
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                file_counts['video'] += 1
            elif ext == '.zip':
                file_counts['zip'] += 1
        for file_type, required_count in requirements.items():
            if file_counts[file_type] != required_count:
                raise ValueError(f"โหมด {mode_id} ต้องการ {file_type} {required_count} ไฟล์, พบ {file_counts[file_type]} ไฟล์")

    def hide_in_image_lsb(self, image, data):
        data_bits = ''.join(format(byte, '08b') for byte in data)
        data_index = 0
        pixels = image.convert('RGB').load()
        width, height = image.size

        if len(data_bits) > width * height:
            raise ValueError("ข้อมูลใหญ่เกินกว่าที่ภาพจะซ่อนได้")

        for x in range(width):
            for y in range(height):
                if data_index >= len(data_bits):
                    break
                r, g, b = pixels[x, y]
                if data_index < len(data_bits):
                    r = (r & ~1) | int(data_bits[data_index])
                    data_index += 1
                pixels[x, y] = (r, g, b)
        return image

    def extract_from_image_lsb(self, image):
        pixels = image.convert('RGB').load()
        width, height = image.size
        data_bits = []
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                data_bits.append(str(r & 1))
                if len(data_bits) >= 8 * 1024:  # จำกัดขนาดข้อมูล
                    break
        data = bytearray()
        for i in range(0, len(data_bits), 8):
            byte = data_bits[i:i+8]
            if len(byte) == 8:
                data.append(int(''.join(byte), 2))
        return bytes(data)

    def execute_mode1(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password'].encode() or Fernet.generate_key()
        fernet = Fernet(Fernet.generate_key() if workflow_item.config['random_aes'] else base64.urlsafe_b64encode(hashlib.sha256(password).digest()))

        encrypted_text = fernet.encrypt(text)
        half_len = len(encrypted_text) // 2
        part1, part2 = encrypted_text[:half_len], encrypted_text[half_len:]

        self.validate_files(workflow_item.source_files, 1)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]

        image = Image.open(image_file)
        encoded_image = self.hide_in_image_lsb(image, part1)
        encoded_image.save(os.path.join(output_path, "stego_image.png"))

        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': base64.b64encode(part2).decode()})

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ ({os.path.basename(image_file)}), เสียง ({os.path.basename(audio_file)})"

    def extract_mode1(self, files, config):
        self.validate_files(files, 1)
        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]

        image = Image.open(image_file)
        part1 = self.extract_from_image_lsb(image)

        audio = pydub.AudioSegment.from_file(audio_file)
        metadata = audio.get_tags() or {}
        part2 = base64.b64decode(metadata.get('comment', ''))

        encrypted_text = part1 + part2
        password = config.get('aes_password', '').encode()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode2(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        docx_password = workflow_item.config['docx_password'] or Fernet.generate_key().decode()
        rsa_key_path = workflow_item.config['rsa_public_key']
        self.validate_files(workflow_item.source_files, 2)
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        doc = docx.Document()
        doc.add_paragraph(text.decode())
        docx_path = os.path.join(output_path, "stego_doc.docx")
        doc.save(docx_path)

        with open(rsa_key_path, 'rb') as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        encrypted_text = public_key.encrypt(
            text,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(encrypted_text).decode()})

        return f"ซ่อนข้อมูลสำเร็จ: วิดีโอ ({os.path.basename(video_file)}), DOCX ({os.path.basename(docx_path)})"

    def extract_mode2(self, files, config):
        self.validate_files(files, 2)
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]
        rsa_private_key_path = config.get('rsa_private_key')
        rsa_password = config.get('rsa_password', '').encode()

        video = mp.VideoFileClip(video_file)
        encrypted_text = base64.b64decode(video.metadata.get('comment', ''))

        with open(rsa_private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=rsa_password)
        decrypted_text = private_key.decrypt(
            encrypted_text,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        return decrypted_text.decode()

    def execute_mode3(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password_m3'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))

        encrypted_text = fernet.encrypt(text)
        if workflow_item.config.get('equal_split', True):
            part_size = len(encrypted_text) // 3
            parts = [encrypted_text[i:i+part_size] for i in range(0, len(encrypted_text), part_size)]
            if len(parts) > 3:
                parts[2] += parts[3]
                parts = parts[:3]
        else:
            image_ratio = workflow_item.config['image_ratio'] / 100
            audio_ratio = workflow_item.config['audio_ratio'] / 100
            video_ratio = workflow_item.config['video_ratio'] / 100
            total_len = len(encrypted_text)
            image_size = int(total_len * image_ratio)
            audio_size = int(total_len * audio_ratio)
            parts = [
                encrypted_text[:image_size],
                encrypted_text[image_size:image_size+audio_size],
                encrypted_text[image_size+audio_size:]
            ]

        self.validate_files(workflow_item.source_files, 3)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        encoded_image = self.hide_in_image_lsb(image, parts[0])
        encoded_image.save(os.path.join(output_path, "stego_image.png"))

        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': base64.b64encode(parts[1]).decode()})

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(parts[2]).decode()})

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ, เสียง, วิดีโอ"

    def extract_mode3(self, files, config):
        self.validate_files(files, 3)
        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        part1 = self.extract_from_image_lsb(image)

        audio = pydub.AudioSegment.from_file(audio_file)
        part2 = base64.b64decode(audio.get_tags().get('comment', ''))

        video = mp.VideoFileClip(video_file)
        part3 = base64.b64decode(video.metadata.get('comment', ''))

        encrypted_text = part1 + part2 + part3
        password = config.get('aes_password_m3', '').encode()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode4(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password_m4'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        encrypted_text = fernet.encrypt(text)

        rsa_key_path = workflow_item.config['rsa_public_key_m4']
        with open(rsa_key_path, 'rb') as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        encrypted_key = public_key.encrypt(
            password,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        self.validate_files(workflow_item.source_files, 4)
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': base64.b64encode(encrypted_text).decode()})

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(encrypted_key).decode()})

        return f"ซ่อนข้อมูลสำเร็จ: เสียง, วิดีโอ"

    def extract_mode4(self, files, config):
        self.validate_files(files, 4)
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]
        rsa_private_key_path = config.get('rsa_private_key_m4')
        rsa_password = config.get('rsa_password_m4', '').encode()

        video = mp.VideoFileClip(video_file)
        encrypted_key = base64.b64decode(video.metadata.get('comment', ''))

        with open(rsa_private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=rsa_password)
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        audio = pydub.AudioSegment.from_file(audio_file)
        encrypted_text = base64.b64decode(audio.get_tags().get('comment', ''))

        fernet = Fernet(aes_key)
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode5(self, workflow_item, output_path):
        text = workflow_item.config['text']
        gpg = gnupg.GPG()
        gpg_key_path = workflow_item.config['gpg_public_key']

        with open(gpg_key_path, 'rb') as key_file:
            gpg.import_keys(key_file.read())
        encrypted_data = gpg.encrypt(text, recipients=None, always_trust=True)

        self.validate_files(workflow_item.source_files, 5)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        image.save(os.path.join(output_path, "stego_image.png"), exif={'Exif.Image.ImageDescription': str(encrypted_data)})

        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': str(encrypted_data)})

        with open(video_file, 'rb') as f:
            video_data = f.read()
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        with open(output_video_path, 'wb') as f:
            f.write(video_data + str(encrypted_data).encode())

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ, เสียง, วิดีโอ"

    def extract_mode5(self, files, config):
        self.validate_files(files, 5)
        gpg = gnupg.GPG()
        gpg_private_key_path = config.get('gpg_private_key')
        gpg_passphrase = config.get('gpg_passphrase')

        with open(gpg_private_key_path, 'rb') as key_file:
            gpg.import_keys(key_file.read(), passphrase=gpg_passphrase)

        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        try:
            image = Image.open(image_file)
            encrypted_data = image.info.get('ImageDescription')
            decrypted_data = gpg.decrypt(encrypted_data, passphrase=gpg_passphrase)
            if decrypted_data.ok:
                return str(decrypted_data)
        except:
            pass

        try:
            audio = pydub.AudioSegment.from_file(audio_file)
            encrypted_data = audio.get_tags().get('comment')
            decrypted_data = gpg.decrypt(encrypted_data, passphrase=gpg_passphrase)
            if decrypted_data.ok:
                return str(decrypted_data)
        except:
            pass

        with open(video_file, 'rb') as f:
            video_data = f.read()
        encrypted_data = video_data[-1024:].decode()
        decrypted_data = gpg.decrypt(encrypted_data, passphrase=gpg_passphrase)
        if decrypted_data.ok:
            return str(decrypted_data)

        raise ValueError("ไม่สามารถถอดข้อมูลได้")

    def execute_mode6(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password_m6'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        encrypted_text = fernet.encrypt(text)

        checksum_algorithm = workflow_item.config['checksum_algorithm']
        checksum = getattr(hashlib, checksum_algorithm.lower())(encrypted_text).hexdigest()

        self.validate_files(workflow_item.source_files, 6)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        encoded_image = self.hide_in_image_lsb(image, encrypted_text)
        encoded_image.save(os.path.join(output_path, "stego_image.png"))

        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': base64.b64encode(password).decode()})

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': checksum})

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ, เสียง, วิดีโอ"

    def extract_mode6(self, files, config):
        self.validate_files(files, 6)
        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        audio = pydub.AudioSegment.from_file(audio_file)
        password = base64.b64decode(audio.get_tags().get('comment', ''))

        image = Image.open(image_file)
        encrypted_text = self.extract_from_image_lsb(image)

        video = mp.VideoFileClip(video_file)
        stored_checksum = video.metadata.get('comment')
        computed_checksum = getattr(hashlib, config.get('checksum_algorithm', 'sha256').lower())(encrypted_text).hexdigest()
        if config.get('verify_checksum') and stored_checksum != computed_checksum:
            raise ValueError("Checksum ไม่ตรงกัน")

        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode7(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        if workflow_item.config['use_base64']:
            text = base64.b64encode(text)
        if workflow_item.config['use_gzip']:
            text = gzip.compress(text)

        password = workflow_item.config['aes_password_m7'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        encrypted_text = fernet.encrypt(text)

        self.validate_files(workflow_item.source_files, 7)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        encoded_image = self.hide_in_image_lsb(image, encrypted_text)
        encoded_image.save(os.path.join(output_path, "stego_image.png"))

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(encrypted_text).decode()})

        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        with open(output_audio_path, 'wb') as f:
            f.write(audio_data + encrypted_text)

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ, เสียง, วิดีโอ"

    def extract_mode7(self, files, config):
        self.validate_files(files, 7)
        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        try:
            image = Image.open(image_file)
            encrypted_text = self.extract_from_image_lsb(image)
        except:
            video = mp.VideoFileClip(video_file)
            encrypted_text = base64.b64decode(video.metadata.get('comment', ''))

        password = config.get('aes_password_m7', '').encode()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        decrypted_text = fernet.decrypt(encrypted_text)

        if config.get('use_gzip', False):
            decrypted_text = gzip.decompress(decrypted_text)
        if config.get('use_base64', False):
            decrypted_text = base64.b64decode(decrypted_text)

        return decrypted_text.decode()

    def execute_mode8(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password_m8'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        encrypted_text = fernet.encrypt(text)

        gpg = gnupg.GPG()
        gpg_key_path = workflow_item.config['gpg_public_key_m8']
        with open(gpg_key_path, 'rb') as key_file:
            gpg.import_keys(key_file.read())
        encrypted_key = gpg.encrypt(password, recipients=None, always_trust=True)

        self.validate_files(workflow_item.source_files, 8)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(encrypted_text).decode()})

        image = Image.open(image_file)
        image.save(os.path.join(output_path, "stego_image.png"), exif={'Exif.Image.ImageDescription': str(encrypted_key)})

        hash_value = hashlib.sha256(encrypted_text).hexdigest()
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        output_audio_path = os.path.join(output_path, "stego_audio.mp3")
        with open(output_audio_path, 'wb') as f:
            f.write(audio_data + hash_value.encode())

        return f"ซ่อนข้อมูลสำเร็จ: ภาพ, เสียง, วิดีโอ"

    def extract_mode8(self, files, config):
        self.validate_files(files, 8)
        image_file = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        gpg = gnupg.GPG()
        gpg_private_key_path = config.get('gpg_private_key_m8')
        gpg_passphrase = config.get('gpg_passphrase_m8')
        with open(gpg_private_key_path, 'rb') as key_file:
            gpg.import_keys(key_file.read(), passphrase=gpg_passphrase)
        image = Image.open(image_file)
        encrypted_key = image.info.get('ImageDescription')
        password = gpg.decrypt(encrypted_key, passphrase=gpg_passphrase)
        if not password.ok:
            raise ValueError("ถอดรหัส GPG ไม่สำเร็จ")

        video = mp.VideoFileClip(video_file)
        encrypted_text = base64.b64decode(video.metadata.get('comment', ''))

        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        stored_hash = audio_data[-64:].decode()
        computed_hash = hashlib.sha256(encrypted_text).hexdigest()
        if stored_hash != computed_hash:
            raise ValueError("Hash ไม่ตรงกัน")

        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(str(password).encode()).digest()))
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode9(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        password = workflow_item.config['aes_password_m9'].encode() or Fernet.generate_key()
        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        encrypted_text = fernet.encrypt(text)

        self.validate_files(workflow_item.source_files, 9)
        image_file = [f for f in workflow_item.source_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][0]
        audio_file = [f for f in workflow_item.source_files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg'))][0]
        video_file = [f for f in workflow_item.source_files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        image = Image.open(image_file)
        encoded_image = self.hide_in_image_lsb(image, encrypted_text)
        temp_image_path = os.path.join(output_path, "temp_image.png")
        encoded_image.save(temp_image_path)

        with open(temp_image_path, 'rb') as f:
            image_data = f.read()
        audio = pydub.AudioSegment.from_file(audio_file)
        output_audio_path = os.path.join(output_path, "temp_audio.mp3")
        audio.export(output_audio_path, format="mp3", tags={'comment': base64.b64encode(image_data).decode()})

        with open(output_audio_path, 'rb') as f:
            audio_data = f.read()
        video = mp.VideoFileClip(video_file)
        output_video_path = os.path.join(output_path, "stego_video.mp4")
        video.write(output_video_path, metadata={'comment': base64.b64encode(audio_data).decode(), 'key': base64.b64encode(password).decode()})

        return f"ซ่อนข้อมูลสำเร็จ: วิดีโอ (มีทุกชั้น)"

    def extract_mode9(self, files, config):
        self.validate_files(files, 9)
        video_file = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))][0]

        video = mp.VideoFileClip(video_file)
        audio_data = base64.b64decode(video.metadata.get('comment', ''))
        password = base64.b64decode(video.metadata.get('key', ''))

        temp_audio_path = os.path.join(os.path.dirname(video_file), "temp_audio.mp3")
        with open(temp_audio_path, 'wb') as f:
            f.write(audio_data)
        audio = pydub.AudioSegment.from_file(temp_audio_path)
        image_data = base64.b64decode(audio.get_tags().get('comment', ''))

        temp_image_path = os.path.join(os.path.dirname(video_file), "temp_image.png")
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        image = Image.open(temp_image_path)
        encrypted_text = self.extract_from_image_lsb(image)

        fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password).digest()))
        decrypted_text = fernet.decrypt(encrypted_text).decode()

        return decrypted_text

    def execute_mode10(self, workflow_item, output_path):
        text = workflow_item.config['text'].encode()
        parts = workflow_item.config['split_parts']
        part_size = len(text) // parts
        text_parts = [text[i:i+part_size] for i in range(0, len(text), part_size)]
        if len(text_parts) > parts:
            text_parts[parts-1] += text_parts[parts]
            text_parts = text_parts[:parts]

        master_password = workflow_item.config['master_password'].encode() or Fernet.generate_key()
        encrypted_parts = []
        for i, part in enumerate(text_parts):
            if workflow_item.config['use_different_keys']:
                key = hashlib.sha256(master_password + str(i).encode()).digest()
            else:
                key = master_password
            fernet = Fernet(base64.urlsafe_b64encode(key))
            encrypted_parts.append(fernet.encrypt(part))

        rsa_keys = workflow_item.config['rsa_key_list']
        encrypted_keys = []
        for key in rsa_keys:
            with open(key, 'rb') as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())
            encrypted_key = public_key.encrypt(
                master_password,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            encrypted_keys.append(encrypted_key)

        timelock_data = {'expire': datetime.now().timestamp() + workflow_item.config['timelock_hours'] * 3600}
        zip_path = os.path.join(output_path, "stego_data.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, part in enumerate(encrypted_parts):
                zipf.writestr(f"part_{i}.bin", part)
            zipf.writestr("keys.bin", b''.join(encrypted_keys))
            zipf.writestr("timelock.json", json.dumps(timelock_data).encode())

        return f"ซ่อนข้อมูลสำเร็จ: ZIP file ({os.path.basename(zip_path)})"

    def extract_mode10(self, files, config):
        self.validate_files(files, 10)
        zip_file = [f for f in files if f.lower().endswith('.zip')][0]
        rsa_keys = [item for item in config.get('rsa_key_list', [])]
        master_password = config.get('master_password', '').encode()

        with zipfile.ZipFile(zip_file, 'r') as zipf:
            timelock_data = json.loads(zipf.read('timelock.json').decode())
            if not config.get('ignore_timelock', False) and datetime.now().timestamp() < timelock_data['expire']:
                raise ValueError("ยังไม่ถึงเวลาปลดล็อก")

            encrypted_keys = zipf.read('keys.bin')
            parts = [zipf.read(f"part_{i}.bin") for i in range(len(files)-1)]

        decrypted_keys = []
        for key_path in rsa_keys:
            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None)
            decrypted_key = private_key.decrypt(
                encrypted_keys[:256],
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            decrypted_keys.append(decrypted_key)
            encrypted_keys = encrypted_keys[256:]

        decrypted_parts = []
        for i, part in enumerate(parts):
            if config.get('use_different_keys', False):
                key = hashlib.sha256(master_password + str(i).encode()).digest()
            else:
                key = master_password
            fernet = Fernet(base64.urlsafe_b64encode(key))
            decrypted_parts.append(fernet.decrypt(part))

        return b''.join(decrypted_parts).decode()

    def execute_mode(self, workflow_item, output_path):
        method = getattr(self, f"execute_mode{workflow_item.mode_id}")
        return method(workflow_item, output_path)

    def extract_mode(self, mode_id, files, config):
        method = getattr(self, f"extract_mode{mode_id}")
        return method(files, config)