import os
import subprocess
import tempfile
import shutil

def gpg_sign_with_keyfile(text_to_sign, private_key_file, passphrase, output_signed_file):
    with tempfile.TemporaryDirectory() as gnupg_home:
        env = os.environ.copy()
        env['GNUPGHOME'] = gnupg_home

        # Import private key
        subprocess.run([
            "gpg", "--batch", "--yes", "--import", private_key_file
        ], env=env, check=True)

        # Write text to sign
        text_file = os.path.join(gnupg_home, "text.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text_to_sign)

        # Sign the text using clearsign
        signed_file = os.path.join(gnupg_home, "signed.asc")
        subprocess.run([
            "gpg", "--batch", "--yes",
            "--pinentry-mode", "loopback",
            "--passphrase", passphrase,
            "--clearsign", "-o", signed_file, text_file
        ], env=env, check=True)

        # Copy signed file to desired output
        shutil.copyfile(signed_file, output_signed_file)
        print("✅ ลายเซ็นถูกสร้างและบันทึกไว้ที่:", output_signed_file)

def gpg_verify_with_keyfile(signed_file, public_key_file):
    with tempfile.TemporaryDirectory() as gnupg_home:
        env = os.environ.copy()
        env['GNUPGHOME'] = gnupg_home

        # Import public key
        subprocess.run([
            "gpg", "--batch", "--yes", "--import", public_key_file
        ], env=env, check=True)

        # Verify signature
        try:
            subprocess.run([
                "gpg", "--verify", signed_file
            ], env=env, check=True)
            print("✅ ลายเซ็นถูกต้อง (Verified)")
        except subprocess.CalledProcessError:
            print("❌ ลายเซ็นไม่ถูกต้อง (Failed to verify)")



def gpg_sign_file(input_file, private_key_file, passphrase, output_signed_file):
    with tempfile.TemporaryDirectory() as gnupg_home:
        env = os.environ.copy()
        env['GNUPGHOME'] = gnupg_home

        # นำเข้า private key
        subprocess.run([
            "gpg", "--batch", "--yes", "--import", private_key_file
        ], env=env, check=True)

        # ลงลายเซ็นไฟล์แบบแยกลายเซ็น (detach-sign)
        subprocess.run([
            "gpg", "--batch", "--yes",
            "--pinentry-mode", "loopback",
            "--passphrase", passphrase,
            "--output", output_signed_file,
            "--detach-sign", input_file
        ], env=env, check=True)

        print(f"✅ ไฟล์ลงลายเซ็นแล้ว -> {output_signed_file}")
        
        
def gpg_verify_file_signature(input_file, signature_file, public_key_file):
    with tempfile.TemporaryDirectory() as gnupg_home:
        env = os.environ.copy()
        env['GNUPGHOME'] = gnupg_home

        # นำเข้า public key
        subprocess.run([
            "gpg", "--batch", "--yes", "--import", public_key_file
        ], env=env, check=True)

        # ตรวจสอบลายเซ็น
        try:
            subprocess.run([
                "gpg", "--verify", signature_file, input_file
            ], env=env, check=True)
            print("✅ ลายเซ็นถูกต้อง (Verified)")
        except subprocess.CalledProcessError:
            print("❌ ลายเซ็นไม่ถูกต้อง (Failed to verify)")







# ----------------------------
# ใช้งาน
private_key = r"C:\Users\65011\Desktop\Segano\work00002\key\private_key_C75DD9D5.asc"
public_key = r"C:\Users\65011\Desktop\Segano\work00002\key\public_key_C75DD9D5.asc"
text = "สวัสดี! ข้อความนี้จะถูกลงลายเซ็นด้วย private key ที่อยู่ในไฟล์กกฟหกฟหกฟหก."
passphrase = "mikkee"  


gpg_sign_with_keyfile(text, private_key, passphrase, "signed.asc")
gpg_verify_with_keyfile("signed2.asc", public_key)



input_file_path = r"C:\Users\65011\Desktop\Segano\work00002\output_files\sad.txt"
signed_output_path = r"C:\Users\65011\Desktop\Segano\work00002\output_files\inputfile.txt.sig"

# ลงลายเซ็นให้กับไฟล์
gpg_sign_file(input_file_path, private_key, passphrase, signed_output_path)

# ตรวจสอบลายเซ็น
gpg_verify_file_signature(input_file_path, signed_output_path, public_key)


