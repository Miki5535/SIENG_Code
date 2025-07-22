
from PIL import Image
import numpy as np
import cv2
import os
from scipy.signal import convolve2d
import struct
import zlib 



def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        return "<font color='green'>"+bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "<font color='red'>ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    
def validate_binary(binary):
    if len(binary) % 8 != 0:
        print(f"Warning: Binary data length ({len(binary)}) is not a multiple of 8")
        binary = binary + '0' * (8 - len(binary) % 8)
    return binary

def binary_to_string_P(binary):
    try:
        binary = validate_binary(binary)
        byte_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        print(f"Decoded Byte Data: {byte_data}")  
        return "<font color='green'>" + byte_data.decode('utf-8', errors='ignore')  
    except UnicodeDecodeError as e:
        print(f"Error decoding UTF-8: {e}") 
        return "<font color='red'>ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"
    except Exception as e:
        print(f"Unexpected error: {e}")  
        return f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}"




def binary_to_string_T(binary):
    try:
        byte_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return byte_data.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"ข้อผิดพลาดในการถอดรหัส UTF-8: {str(e)}")
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    except ValueError as e:
        print(f"ข้อผิดพลาดในการแปลง Binary: {str(e)}")
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"

    
def binary_to_string2(binary):
    try:
        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"






def hide_message_lsb_from_steganography(image_path, message, output_path):
    img = Image.open(image_path).convert('RGB') 
    arr = np.array(img)

    binary_message = string_to_binary(message) + '0' * 8
    required_bits = len(binary_message)

    height, width, channels = arr.shape
    max_bits = height * width * 3
    
    if required_bits > max_bits:
        raise ValueError(f"ข้อความยาวเกินไป! ต้องการ {required_bits} บิต แต่ภาพรองรับได้แค่ {max_bits} บิต")

    idx = 0
    for i in range(height):
        for j in range(width):
            for k in range(3):
                if idx < required_bits:
                    arr[i, j, k] = (arr[i, j, k] & 254) | int(binary_message[idx])
                    idx += 1
                if idx >= required_bits:
                    break
            if idx >= required_bits:
                break
        if idx >= required_bits:
            break

    Image.fromarray(arr).save(output_path, format='PNG')
    print(f"ฝังข้อความสำเร็จ! บันทึกที่ {output_path}")

def hide_message_masking_filtering_from_steganography(image_path, message, output_path):
    """ซ่อนข้อความในบริเวณขอบภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    
    message_bits = string_to_binary(message)
    length_bits = format(len(message_bits), '032b') 
    full_message = length_bits + message_bits  
    bit_idx = 0

    
    edges = cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 100, 200)
    edge_pixels = np.count_nonzero(edges)
    required_bits = len(full_message)

    
    if required_bits > edge_pixels:
        raise ValueError(f"⚠️ ข้อความยาวเกินไป! ต้องใช้ {required_bits} บิต แต่มีแค่ {edge_pixels} บิต")

    embedded_pixels = 0
    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0 and bit_idx < required_bits:
                img[i, j, 0] = (img[i, j, 0] & 0b11111110) | int(full_message[bit_idx])  # ตั้งค่า LSB
                bit_idx += 1
                embedded_pixels += 1
            if bit_idx >= required_bits:
                break
        if bit_idx >= required_bits:
            break

   
    cv2.imwrite(output_path, img)

def hide_message_palette_based_from_steganography(image_path, message, output_path):
    
    img = Image.open(image_path).convert("RGB")
    temp_png_path = "temp_image.png"
    img.save(temp_png_path, format="PNG")
    print(f"Loaded image: {image_path}, temporary PNG created at {temp_png_path}")
    
    try:
        
        img = Image.open(temp_png_path).convert("P")
        palette = img.getpalette()
        print(f"Palette size: {len(palette)}")  
        
        
        binary_message = '0' * 8 + string_to_binary(message) + '0' * 8
        print(f"Binary message length: {len(binary_message)}")  
        
       
        if len(binary_message) > len(palette):
            raise ValueError(f"ข้อความยาวเกินขีดจำกัดของพาเลต (ข้อความ={len(binary_message)} บิต, พาเลต={len(palette)} สี)")
        
        
        for i in range(len(binary_message)):
            if i < len(palette):
                original_value = palette[i]
                palette[i] = (palette[i] & ~1) | int(binary_message[i]) 
                print(f"Embedding bit {binary_message[i]} at palette index {i}: {original_value} -> {palette[i]}")  # Debug
        
        img.putpalette(palette)
        img.save(output_path, format="PNG")
        print(f"Message successfully embedded in {output_path}")

    finally:
        
        if os.path.exists(temp_png_path):
            os.remove(temp_png_path)
            print(f"Temporary file {temp_png_path} removed")
    
def hide_message_alpha_channel(image_path, message, output_path):
    """ซ่อนข้อความในช่อง Alpha ของภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  
    if img is None or img.shape[2] != 4:
        raise ValueError("ภาพต้องเป็น PNG ที่มี Alpha Channel")
    max_bits = img.shape[0] * img.shape[1]
    print(f"🔢 จำนวนบิตสูงสุดที่สามารถฝังได้: {max_bits}")
    binary_message = string_to_binary(message) + '00000000'
    print(f"📏 จำนวนบิตข้อความ: {len(binary_message)}")
    if len(binary_message) > max_bits:
        raise ValueError(f"⚠️ ข้อความยาวเกินกว่าที่จะฝังได้! จำนวนบิตสูงสุดที่สามารถฝังได้: {max_bits}")
    idx = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if idx < len(binary_message):
                alpha = np.uint8(img[i, j, 3])
                new_alpha = np.uint8((alpha & 0xFE) | int(binary_message[idx]))  # ใช้ 0xFE แทน ~1
                img[i, j, 3] = new_alpha
                
                idx += 1
            else:
                break
        if idx >= len(binary_message):
            break

    cv2.imwrite(output_path, img)
    print(f"ข้อความถูกซ่อนใน: {output_path}")

def hide_message_edge_detection(image_path, message, output_path):
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
        message_bytes = message.encode('utf-8')
        checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        header = struct.pack('>II', len(message_bytes), checksum)
        full_data = header + message_bytes
        return ''.join(format(b, '08b') for b in full_data)
    
    edges = sobel_edges(gray_array)
    edge_pixels = np.count_nonzero(edges)
    print(f"🔍 จำนวนพิกเซลขอบที่ใช้ได้: {edge_pixels}")
    
    binary_message = prepare_message(message)
    total_bits = len(binary_message)
    print(f"📏 จำนวนบิตข้อความ (รวม header): {total_bits}")
    
    
    img2 = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img2 is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    edges2 = cv2.Canny(gray_img2, 100, 200)  

    edge_pixels2 = np.count_nonzero(edges2)
    
    
    if total_bits > edge_pixels2:
        raise ValueError(f"⚠️ ข้อความยาวเกินกว่าที่จะฝังในขอบของภาพได้! (ต้องการ {total_bits} bits, มี {edge_pixels2} bits)")
    
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



















def retrieve_message_lsb_from_steganography(image_path):
    img = Image.open(image_path)
    arr = np.array(img)

    binary_message = ""
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(min(3, arr.shape[2])):
                binary_message += str(arr[i, j, k] & 1)
                if len(binary_message) % 8 == 0 and len(binary_message) >= 8:
                    if binary_message[-8:] == '00000000':
                        return binary_to_string(binary_message[:-8])
    return None

def retrieve_message_palette_based_from_steganography(image_path):
    img = Image.open(image_path).convert("P")
    palette = img.getpalette()
    print(f"Loaded image: {image_path}, Palette size: {len(palette)}")

    binary_message = ''.join(str(color & 1) for color in palette[:len(palette)])
    print(f"Extracted binary message (length={len(binary_message)}): {binary_message[:64]}...")  # Debug: แสดง binary ส่วนแรก


    if binary_message.count('00000000') >= 2:
        binary_parts = binary_message.split('00000000')
        print(f"Binary parts split by delimiter: {binary_parts}")

        if len(binary_parts) > 2:
            binary_message = binary_parts[1]
            print(f"Binary message extracted: {binary_message}")
            return binary_to_string_P(binary_message)
    else:
        print("Delimiter not found in binary message")
    
    return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"

def retrieve_message_alpha_channel(image_path):
    """ดึงข้อความที่ซ่อนไว้ในช่อง Alpha ของภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        raise ValueError("ภาพต้องเป็น PNG ที่มี Alpha Channel")

    binary_message = ''
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            
            alpha = np.uint8(img[i, j, 3])
            binary_message += str(alpha & 1)
            
            
            if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':
                return binary_to_string(binary_message[:-8])
    return binary_to_string(binary_message)

def retrieve_message_edge_detection(image_path):
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
        
        
        header_bits = ""
        for i, j in edge_positions[:64]:
            header_bits += str(img_array[i, j, 0] & 1)
        
        
        header_bytes = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
        message_length, expected_checksum = struct.unpack('>II', header_bytes)
        
        
        total_bits_needed = 64 + (message_length * 8)  
        binary_message = header_bits
        
        for i, j in edge_positions[64:total_bits_needed]:
            binary_message += str(img_array[i, j, 0] & 1)
        
        
        message_binary = binary_message[64:]
        message_bytes = bytes(int(message_binary[i:i+8], 2) 
                            for i in range(0, len(message_binary), 8))
        
        
        actual_checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        if actual_checksum != expected_checksum:
            return "<font color='red'>⚠️ ข้อมูลเสียหาย: Checksum ไม่ตรงกัน</font>"
        
        return message_bytes.decode('utf-8')
        
    except (struct.error, ValueError, UnicodeDecodeError) as e:
        return f"<font color='red'>⚠️ เกิดข้อผิดพลาด: {str(e)}</font>"
    except Exception as e:
        return f"<font color='red'>⚠️ ข้อผิดพลาดที่ไม่คาดคิด: {str(e)}</font>"


def retrieve_message_masking_filtering_from_steganography(image_path):
    """ดึงข้อความที่ซ่อนไว้ในขอบภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    edges = cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 100, 200)
    binary_message = ""
    length = None  

    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0:
                binary_message += str(img[i, j, 0] & 1)
                if length is None and len(binary_message) == 32:
                    length = int(binary_message, 2)
                    binary_message = "" 
                elif length is not None and len(binary_message) == length:
                    return binary_to_string(binary_message)
    return "ไม่มีข้อความ หรือข้อมูลผิดพลาด"























