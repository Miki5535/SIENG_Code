import cv2
import numpy as np
from PIL import Image
import numpy as np
from scipy.signal import convolve2d
import struct
import zlib 



def hide_message_edge_detection_pil(image_path, message, output_path):
    """ซ่อนข้อความในภาพโดยใช้การตรวจจับขอบด้วย PIL"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    
    def sobel_edges(gray):
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2)
        threshold = 30
        return edges > threshold
    
    def prepare_message(message):
        # เข้ารหัสข้อความเป็น UTF-8
        message_bytes = message.encode('utf-8')
        # คำนวณ checksum
        checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        # เตรียมส่วนหัว: ความยาว (4 bytes) + checksum (4 bytes)
        header = struct.pack('>II', len(message_bytes), checksum)
        # รวมส่วนหัวและข้อความ
        full_data = header + message_bytes
        # แปลงเป็น binary string
        return ''.join(format(b, '08b') for b in full_data)
    
    # ตรวจจับขอบ
    edges = sobel_edges(gray_array)
    edge_pixels = np.count_nonzero(edges)
    print(f"🔍 จำนวนพิกเซลขอบที่ใช้ได้: {edge_pixels}")
    
    # เตรียมข้อความ
    binary_message = prepare_message(message)
    total_bits = len(binary_message)
    print(f"📏 จำนวนบิตข้อความ (รวม header): {total_bits}")
    
    if total_bits > edge_pixels:
        raise ValueError(f"⚠️ ข้อความยาวเกินกว่าที่จะฝังในขอบของภาพได้! (ต้องการ {total_bits} bits, มี {edge_pixels} bits)")
    
    # ฝังข้อมูล
    edge_positions = np.column_stack(np.where(edges))
    for bit_idx, (i, j) in enumerate(edge_positions[:total_bits]):
        if bit_idx < total_bits:
            pixel_value = img_array[i, j, 0]
            new_value = (pixel_value & 0xFE) | int(binary_message[bit_idx])
            img_array[i, j, 0] = new_value
    
    print(f"📊 จำนวนพิกเซลที่ใช้ในการฝังข้อมูล: {total_bits}")
    print(f"💾 ข้อมูลทั้งหมดที่ฝัง: {total_bits} บิต")
    
    result_img = Image.fromarray(img_array)
    result_img.save(output_path)
    print(f"✅ ข้อความถูกซ่อนใน: {output_path}")

def extract_message_pil(image_path):
    """ดึงข้อความที่ซ่อนอยู่ในภาพ"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    
    def sobel_edges(gray):
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2)
        threshold = 30
        return edges > threshold
    
    try:
        edges = sobel_edges(gray_array)
        edge_positions = np.column_stack(np.where(edges))
        
        # อ่าน header ก่อน (8 bytes = 64 bits)
        header_bits = ""
        for i, j in edge_positions[:64]:
            header_bits += str(img_array[i, j, 0] & 1)
        
        # แปลง header bits เป็น bytes
        header_bytes = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
        message_length, expected_checksum = struct.unpack('>II', header_bytes)
        
        # อ่านข้อความตามความยาวที่ระบุ
        total_bits_needed = 64 + (message_length * 8)  # header + message
        binary_message = header_bits
        
        for i, j in edge_positions[64:total_bits_needed]:
            binary_message += str(img_array[i, j, 0] & 1)
        
        # แยกส่วน message
        message_binary = binary_message[64:]
        message_bytes = bytes(int(message_binary[i:i+8], 2) 
                            for i in range(0, len(message_binary), 8))
        
        # ตรวจสอบ checksum
        actual_checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        if actual_checksum != expected_checksum:
            return "<font color='red'>⚠️ ข้อมูลเสียหาย: Checksum ไม่ตรงกัน</font>"
        
        return message_bytes.decode('utf-8')
        
    except (struct.error, ValueError, UnicodeDecodeError) as e:
        return f"<font color='red'>⚠️ เกิดข้อผิดพลาด: {str(e)}</font>"
    except Exception as e:
        return f"<font color='red'>⚠️ ข้อผิดพลาดที่ไม่คาดคิด: {str(e)}</font>"

# ฟังก์ชั่นช่วยคำนวณขนาดข้อความและพื้นที่ที่ใช้ได้
def calculate_message_capacity(image_path, message):
    """คำนวณขนาดข้อความและพื้นที่ที่ใช้ได้ในภาพ"""
    img = Image.open(image_path).convert('RGB')
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    
    def sobel_edges(gray):
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2)
        threshold = 30
        return edges > threshold
    
    edges = sobel_edges(gray_array)
    available_bits = np.count_nonzero(edges)
    
    message_bytes = message.encode('utf-8')
    header_size = 8  # 4 bytes length + 4 bytes checksum
    total_bytes = header_size + len(message_bytes)
    total_bits = total_bytes * 8
    
    return total_bits, available_bits

def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    






# ทดสอบ
image_path = r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds.png"
output_path=r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds_outtttt.png"
# message = "ผมชื่อ mikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกฟหกกกกกกกmikiหฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกกวว"
message = "ผมชื่อ mikiหฟกฟกฟกdsdsdsดดดดดดดดดดasdddddddดดดดดดdddddddddดดกหหหหหหหหหหหหหหหหหหหหหหหหหหหdsdกหดดดดดดดดดดดดดดดsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsdsกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟกฟ"

# message = "ผมชื่อ mikiหฟกฟกฟกdsdsdsดดดดดdasssssssดดดดดดดดดด"
# hide_message_edge_detection(image_path, message, output_path)
# print(extract_message_edge_detection(output_path))


# ตรวจสอบความจุก่อน
bit_length, available_bits = calculate_message_capacity(image_path, message)
print(f"ต้องการใช้: {bit_length} bits")
print(f"มีพื้นที่: {available_bits} bits")

# ซ่อนข้อความ
hide_message_edge_detection_pil(image_path, message, output_path)

# ถอดข้อความ
extracted_message = extract_message_pil(output_path)
print(extracted_message)