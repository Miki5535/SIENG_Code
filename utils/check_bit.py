
import os
from PIL import Image
import cv2
import numpy as np



def check_bit_message(message,previous_text_length,num):
    current_length = len(''.join(format(byte, '08b') for byte in message.encode('utf-8')))

    # กรณีที่ข้อความเป็นช่องว่างหรือข้อความทั้งหมดถูกลบ
    if current_length == 0 and previous_text_length > 0:
        num += previous_text_length  # เพิ่ม num เมื่อข้อความถูกลบทั้งหมด
    # กรณีข้อความถูกเพิ่ม
    elif current_length > previous_text_length:
        num -= (current_length - previous_text_length)  # ลด num ตามจำนวนข้อความที่เพิ่ม
    # กรณีข้อความถูกลบ
    elif current_length < previous_text_length:
        num += (previous_text_length - current_length)  # เพิ่ม num ตามจำนวนข้อความที่ถูกลบ
        

    if num < 0:
        setText=f"bit เกิน {abs(num)}"
        setStyleSheet ="color: red; font-weight: bold; font-size: 34px; background-color: transparent;"
    else:
        # อัปเดตข้อความแสดงจำนวนตัวอักษรที่ใส่ได้
        setText=f"bit เหลือ {abs(num)}"
        setStyleSheet ="color: green; font-weight: bold; font-size: 34px; background-color: transparent;"

    return num,setText,setStyleSheet,current_length


def check_bit_palette(image_path):
    img = Image.open(image_path).convert("RGB")
    temp_png_path = "temp_image.png"
    img.save(temp_png_path, format="PNG")
    try:
        img = Image.open(temp_png_path).convert("P")
        palette = img.getpalette()
        print(f"check_bit_palette ==> Palette size: {len(palette)}")
    finally:
        if os.path.exists(temp_png_path):
            os.remove(temp_png_path)
    return len(palette)-16

def check_bit_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    height, width, channels = arr.shape
    max_bits = height * width * 3
    return max_bits-8


def check_bit_edge_detection(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_img, 100, 200)
    edge_pixels = np.count_nonzero(edges)
    return edge_pixels-64


def check_bit_alpha_channel(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        return 0
    max_bits = img.shape[0] * img.shape[1]
    print(f"🔢 จำนวนบิตสูงสุดที่สามารถฝังได้: {max_bits}")
    return max_bits-8



def check_bit_masking_filtering(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    edges = cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 100, 200)
    edge_pixels = np.count_nonzero(edges)
    return edge_pixels-32
    















