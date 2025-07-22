import os
import shutil
import struct


def append_files_to_image(image_path, files_to_append):
    """
    Append files to an image and add a marker.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"ไม่พบไฟล์ภาพ: {image_path}")

    modified_image_path = os.path.splitext(image_path)[0] + "_modified.png"
    shutil.copy2(image_path, modified_image_path)

    try:
        with open(modified_image_path, 'ab') as image_file:
            marker = b"APPEND_START"
            image_file.write(marker)  # Write marker
            print("Marker written successfully.")

            image_file.write(struct.pack('<I', len(files_to_append)))  # Number of files
            print(f"Number of files to append: {len(files_to_append)}")

            for file_path in files_to_append:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue

                file_ext = os.path.splitext(file_path)[1][1:].encode('ascii', errors='ignore').decode('ascii')
                with open(file_path, 'rb') as append_file:
                    file_data = append_file.read()

                # Write file metadata and content
                image_file.write(struct.pack('<I', len(file_ext)))
                image_file.write(file_ext.encode('ascii'))
                image_file.write(struct.pack('<Q', len(file_data)))
                image_file.write(file_data)
                print(f"Appended file: {file_path}")

        return modified_image_path

    except Exception as e:
        raise e


def extract_appended_files(image_path, output_dir):
    """
    Extract appended files from an image with a marker.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"ไม่พบไฟล์ภาพ: {image_path}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(image_path, 'rb') as image_file:
            image_file.seek(0, os.SEEK_END)
            total_size = image_file.tell()

            # Search for the marker in the last few kilobytes of the image file
            marker = b"APPEND_START"
            marker_found = False
            buffer_size = 8192  # Buffer size to search through, can be increased for larger files
            for i in range(total_size - buffer_size, total_size):
                image_file.seek(i)
                data = image_file.read(len(marker))
                if data == marker:
                    marker_found = True
                    break

            if not marker_found:
                raise ValueError("ไม่พบ marker ที่ระบุจุดเริ่มต้นของไฟล์ที่ถูกต่อท้าย")

            # Once marker is found, read the appended file metadata and content
            append_start = i + len(marker)
            image_file.seek(append_start)

            num_files = struct.unpack('<I', image_file.read(4))[0]
            print(f"Number of appended files: {num_files}")

            extracted_files = []
            for _ in range(num_files):
                ext_len = struct.unpack('<I', image_file.read(4))[0]
                file_ext = image_file.read(ext_len).decode('ascii')
                file_size = struct.unpack('<Q', image_file.read(8))[0]
                file_data = image_file.read(file_size)

                output_file = os.path.join(output_dir, f"extracted_file_{_ + 1}.{file_ext}")
                with open(output_file, 'wb') as output:
                    output.write(file_data)
                extracted_files.append(output_file)
                print(f"Extracted file: {output_file}")

            return extracted_files

    except Exception as e:
        print(f"Error occurred: {e}")
        raise e




# ตัวอย่างการต่อท้ายไฟล์
image_path = r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds.png"
files_to_append = [r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\ztxt.txt", r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\zzzzdf.docx"]
modified_image = append_files_to_image(image_path, files_to_append)
print(f"ไฟล์ภาพที่ถูกต่อท้ายถูกบันทึกไว้ที่: {modified_image}")

# ตัวอย่างการถอดไฟล์ที่ถูกต่อท้าย
output_dir = r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds_modified_out.png"
extracted_files = extract_appended_files(modified_image, output_dir)
print("ไฟล์ที่ถูกถอดออกมา:")
for file in extracted_files:
    print(file)

