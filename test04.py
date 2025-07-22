import cv2
import numpy as np
from scipy.fftpack import dct, idct

def string_to_binary(message):
    try:
        # Add start marker and end marker
        message_bytes = message.encode('utf-8')
        # Add start marker (0xFF) and end marker (0xFE)
        marked_message = b'\xFF' + message_bytes + b'\xFE'
        return ''.join(format(byte, '08b') for byte in marked_message)
    except UnicodeEncodeError:
        raise ValueError("ไม่สามารถแปลงข้อความเป็นรหัสไบนารีได้ กรุณาตรวจสอบข้อความ")

def binary_to_string(binary_message):
    try:
        # Convert binary to bytes
        message_bytes = bytes(int(binary_message[i:i+8], 2) for i in range(0, len(binary_message), 8))
        
        # Find start marker and end marker
        start_idx = message_bytes.find(b'\xFF')
        end_idx = message_bytes.find(b'\xFE', start_idx)
        
        if start_idx == -1 or end_idx == -1:
            return "ไม่พบข้อความที่ซ่อนอยู่"
        
        # Extract the actual message
        actual_message = message_bytes[start_idx+1:end_idx]
        return actual_message.decode('utf-8')
    except UnicodeDecodeError:
        return "ไม่สามารถถอดรหัสข้อความได้ ข้อมูลอาจเสียหาย"
    except ValueError:
        return "รูปแบบข้อมูลไบนารีไม่ถูกต้อง"

def calculate_max_bits(img_shape):
    max_bits = (img_shape[0] // 8) * (img_shape[1] // 8) * 6
    print(f"จำนวนบิตสูงสุดที่สามารถซ่อนได้: {max_bits} บิต")
    # คำนวณจำนวนตัวอักษรโดยประมาณ (หารด้วย 24 เพราะตัวอักษรไทยใช้ประมาณ 3 ไบต์)
    approx_thai_chars = max_bits // 24
    print(f"สามารถซ่อนข้อความภาษาไทยได้ประมาณ: {approx_thai_chars} ตัวอักษร")
    return max_bits

def check_image_size(img_shape):
    min_size = 8
    if img_shape[0] < min_size or img_shape[1] < min_size:
        raise ValueError(f"ขนาดภาพเล็กเกินไป! ขนาดขั้นต่ำคือ {min_size}x{min_size} พิกเซล")
    print(f"ขนาดภาพถูกต้อง: {img_shape[0]}x{img_shape[1]} พิกเซล")

def hide_message(image_path, message, output_path):
    # Convert message to binary with markers
    binary_message = string_to_binary(message)
    print(f"ความยาวข้อความในรูปแบบไบนารี: {len(binary_message)} บิต")
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้ กรุณาตรวจสอบที่อยู่ไฟล์")
    
    check_image_size(img.shape)
    max_bits = calculate_max_bits(img.shape)
    
    if len(binary_message) > max_bits:
        raise ValueError(f"ข้อความยาวเกินไป! ความจุสูงสุดคือ {max_bits} บิต")
    
    img_float = np.float32(img)
    block_size = 8
    height, width = img.shape
    dct_blocks = np.zeros_like(img_float)
    
    for i in range(0, height - block_size + 1, block_size):
        for j in range(0, width - block_size + 1, block_size):
            block = img_float[i:i+block_size, j:j+block_size]
            dct_blocks[i:i+block_size, j:j+block_size] = cv2.dct(block)
    
    msg_idx = 0
    for i in range(0, height - block_size + 1, block_size):
        for j in range(0, width - block_size + 1, block_size):
            if msg_idx < len(binary_message):
                bit = int(binary_message[msg_idx])
                coef = dct_blocks[i+1, j+1]
                dct_blocks[i+1, j+1] = np.floor(coef) + (0.5 if bit == 1 else 0)
                msg_idx += 1
    
    stego_img = np.zeros_like(img_float)
    for i in range(0, height - block_size + 1, block_size):
        for j in range(0, width - block_size + 1, block_size):
            block = dct_blocks[i:i+block_size, j:j+block_size]
            stego_img[i:i+block_size, j:j+block_size] = cv2.idct(block)
    
    stego_img = np.clip(stego_img, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, stego_img)
    print(f"บันทึกภาพที่ซ่อนข้อความแล้วที่: {output_path}")

def retrieve_message(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้ กรุณาตรวจสอบที่อยู่ไฟล์")
    
    check_image_size(img.shape)
    img_float = np.float32(img)
    block_size = 8
    height, width = img.shape
    dct_blocks = np.zeros_like(img_float)
    
    for i in range(0, height - block_size + 1, block_size):
        for j in range(0, width - block_size + 1, block_size):
            block = img_float[i:i+block_size, j:j+block_size]
            dct_blocks[i:i+block_size, j:j+block_size] = cv2.dct(block)
    
    binary_message = ""
    for i in range(0, height - block_size + 1, block_size):
        for j in range(0, width - block_size + 1, block_size):
            coef = dct_blocks[i+1, j+1]
            bit = '1' if (coef % 1) >= 0.25 else '0'
            binary_message += bit
            
            # Check for end marker in the binary message
            if len(binary_message) >= 16:  # At least should have start marker and end marker
                try:
                    decoded = binary_to_string(binary_message)
                    if decoded != "ไม่พบข้อความที่ซ่อนอยู่" and decoded != "ไม่สามารถถอดรหัสข้อความได้ ข้อมูลอาจเสียหาย":
                        return decoded
                except:
                    continue
    
    return "ไม่พบข้อความที่ซ่อนอยู่"

# Example usage
if __name__ == "__main__":
    image_path = r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\test01.png"
    output_path = r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\test01_stego.png"
    secret_message = "สวัสดีชาวโลกdfsssssssssssssssssssssssssssหกดเหกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกกดดดดดดดดดดดดดดดดดดดดดดดดดดดดดดดดด"
    
    try:
        hide_message(image_path, secret_message, output_path)
        retrieved_message = retrieve_message(output_path)
        print(f"ข้อความที่ถอดรหัสได้: {retrieved_message}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
