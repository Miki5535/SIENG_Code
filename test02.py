import cv2
import os

# ฟังก์ชันแปลงข้อความเป็น Binary
def string_to_binary(s):
    return ''.join(f"{byte:08b}" for byte in s.encode('utf-8'))

# ฟังก์ชันแปลง Binary กลับเป็นข้อความ
def binary_to_string(b):
    byte_data = bytes(int(b[i:i+8], 2) for i in range(0, len(b), 8))
    return byte_data.decode('utf-8', errors='ignore')

# ฟังก์ชันซ่อนข้อความในวิดีโอ
def encode_message_in_video(input_video, output_video, message):
    # เพิ่ม End Marker
    binary_message = string_to_binary(message) + '1111111111111110'
    total_bits = len(binary_message)
    
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print("❌ ไม่สามารถเปิดไฟล์วิดีโอต้นฉบับได้")
        return

    # ดึงค่า properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    # ปรับให้ความกว้าง-สูงเป็นเลขคู่ (บาง Codec ต้องการ)
    width = width if width % 2 == 0 else width + 1
    height = height if height % 2 == 0 else height + 1

    # ใช้ codec FFV1 (lossless) พร้อมนามสกุล .avi
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("❌ ไม่สามารถสร้างไฟล์วิดีโอขาออกได้")
        cap.release()
        return

    message_idx = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if message_idx < total_bits:
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    if message_idx < total_bits:
                        # แก้ไข LSB ของ red channel
                        frame[i, j, 0] = (frame[i, j, 0] & 0xFE) | int(binary_message[message_idx])
                        message_idx += 1
                    else:
                        break
                else:
                    continue
                break
        
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    print(f"✅ ซ่อนข้อความแล้ว: {message_idx}/{total_bits} บิต")
    print(f"🎞️ จำนวนเฟรมทั้งหมด: {frame_count}")

# ฟังก์ชันถอดข้อความจากวิดีโอ
def decode_message_from_video(encoded_video):
    cap = cv2.VideoCapture(encoded_video)
    if not cap.isOpened():
        print("❌ ไม่สามารถเปิดวิดีโอที่ฝังข้อความได้")
        return ""

    binary_message = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                binary_message += str(frame[i, j, 0] & 1)
                if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                    cap.release()
                    return binary_to_string(binary_message[:-16])
    
    cap.release()
    return binary_to_string(binary_message)

# ฟังก์ชันหลัก (ไม่ต้องใช้เสียงแล้ว)
if __name__ == "__main__":
    # input_video = r'C:\Users\65011\Desktop\Segano\work00002\vdio\avi.avi'
    input_video = r'C:\Users\65011\Desktop\Segano\work00002\vdio\mm.mp4'
    output_video = r'C:\Users\65011\Desktop\Segano\work00002\vdio\mm_hidden.avi'
    message = "ทดสอบการซ่อนข้อความ ssdsad 15516"

    print("📦 กำลังซ่อนข้อความลงในวิดีโอ...")
    encode_message_in_video(input_video, output_video, message)

    print("🔍 กำลังถอดข้อความที่ซ่อน...")
    extracted = decode_message_from_video(output_video)
    print(f"📤 ข้อความที่ถอดได้: {extracted}")

    if extracted == message:
        print("✅ ข้อความถูกต้อง 100%")
    else:
        print("❌ ข้อความไม่ตรง กรุณาตรวจสอบ")