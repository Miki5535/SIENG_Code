import os
import subprocess
import sys

def run_exe(relative_path):
    try:
        # หาเส้นทางปัจจุบันของไฟล์นี้
        current_directory = os.path.dirname(os.path.realpath(__file__))
        
        # คำนวณเส้นทางเต็มของไฟล์ที่ต้องการรัน
        file_path = os.path.join(current_directory, relative_path)
        
        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # ตรวจสอบนามสกุลไฟล์
        if file_path.endswith(".py"):
            # ใช้ Python Interpreter สำหรับรันไฟล์ .py
            result = subprocess.run([sys.executable, file_path], capture_output=True, text=True)
        else:
            # ใช้รันไฟล์ EXE หรือไฟล์อื่น
            result = subprocess.run([file_path], capture_output=True, text=True, shell=True)
        
        # แสดงผลลัพธ์
        print("Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Error:")
            print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

# ตัวอย่างการเรียกใช้งาน
run_exe("main.py")  # หรือ "example.exe"
