import cv2
import numpy as np
import os
import subprocess
import shutil

def hide_message_in_image(img, message):
    # แปลงข้อความเป็น bytes ด้วย utf-8 + sentinel
    message_bytes = message.encode('utf-8')
    sentinel = b'\xff\xfe'  # sentinel สำหรับบอกจบข้อความ
    data = bytearray(message_bytes + sentinel)

    index = 0
    bit_pos = 0  # ตำแหน่ง bit ใน byte ปัจจุบัน
    rows, cols, _ = img.shape

    for i in range(rows):
        for j in range(cols):
            for k in range(3):  # R, G, B
                if index < len(data):
                    # ดึง bit ที่ position bit_pos จาก byte[index]
                    bit = (data[index] >> (7 - bit_pos)) & 1
                    # ใส่ bit ลงใน LSB ของ pixel
                    img[i, j, k] = (img[i, j, k] & 0xFE) | bit

                    bit_pos += 1
                    if bit_pos == 8:
                        index += 1
                        bit_pos = 0
                else:
                    return img
    return img

def extract_message_from_image(img):
    bits = []
    sentinel = b'\xff\xfe'
    current_byte = 0
    bit_count = 0
    extracted_bytes = bytearray()

    rows, cols, _ = img.shape

    for i in range(rows):
        for j in range(cols):
            for k in range(3):  # R, G, B
                lsb = img[i, j, k] & 1
                bits.append(lsb)
                current_byte = (current_byte << 1) | lsb
                bit_count += 1

                if bit_count == 8:
                    extracted_bytes.append(current_byte & 0xFF)
                    current_byte = 0
                    bit_count = 0

                    # ตรวจจับ sentinel
                    if len(extracted_bytes) >= 2 and extracted_bytes[-2:] == sentinel:
                        print("✅ Found sentinel at index", len(extracted_bytes) - 2)
                        extracted_bytes = extracted_bytes[:-2]  # ลบ sentinel ออก
                        try:
                            return extracted_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            return "❌ ไม่สามารถถอดรหัสข้อความได้"

    # หากไม่เจอ sentinel
    print("⚠️ ไม่เจอ sentinel ตอนดึงข้อความ")
    try:
        return extracted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return "❌ ไม่สามารถถอดรหัสข้อความได้"


# 🎬 1. Extract frames
def extract_frames(input_video, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)
    subprocess.run(['ffmpeg', '-y', '-i', input_video, f'{output_folder}/frame_%05d.png'])

# 🎞 2. Encode message into last frame
def encode_message_to_last_frame(output_folder, message):
    frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
    last_frame_path = os.path.join(output_folder, frames[-1])
    img = cv2.imread(last_frame_path)
    img_encoded = hide_message_in_image(img, message)
    cv2.imwrite(last_frame_path, img_encoded)

# 🎥 3. Combine frames + original audio
def combine_frames_to_video(output_folder, original_video, output_video):
    cmd = ['ffprobe', '-v', '0', '-of', 'csv=p=0', '-select_streams', 'v:0',
           '-show_entries', 'stream=r_frame_rate', original_video]
    result = subprocess.run(cmd, capture_output=True, text=True)
    framerate = result.stdout.strip()
    if '/' in framerate:
        num, den = map(int, framerate.split('/'))
        fps = num / den
    else:
        fps = float(framerate)

    subprocess.run([
        'ffmpeg', '-y', '-framerate', str(fps), '-i',
        f'{output_folder}/frame_%05d.png',
        '-i', original_video,
        '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy', output_video
    ])

# 🎯 ตัวอย่างการใช้
if __name__ == "__main__":
    output_folder = "frames"
    input_video = r"C:\Users\65011\Desktop\Segano\work00002\vdio\avi.avi"
    output_video = r"C:\Users\65011\Desktop\Segano\work00002\vdio\output\out_video2.mp4"
    secret_message = "mikkeeหกหฟก222aหหหหหห"

    extract_frames(input_video, output_folder)
    encode_message_to_last_frame(output_folder, secret_message)
    combine_frames_to_video(output_folder, input_video, output_video)

    print("✅ Finished embedding secret message in the last frame.")

    # ทดสอบอ่านกลับจากเฟรมสุดท้าย
    frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
    last_frame_path = os.path.join(output_folder, frames[-1])
    img = cv2.imread(last_frame_path)
    recovered_message = extract_message_from_image(img)
    print("📤 Extracted message:", recovered_message)
