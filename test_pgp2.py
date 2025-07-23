import os
import subprocess
import tempfile
import shutil

def run_command(command, gpg_home=None):
    env = os.environ.copy()
    if gpg_home:
        env['GNUPGHOME'] = gpg_home
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
    return result

def gpg_sign_with_keyfile(message_text, private_key_path):
    with tempfile.TemporaryDirectory() as gnupg_temp_home:
        print(f"[INFO] Temporary GNUPGHOME: {gnupg_temp_home}")

        # Import private key
        import_result = run_command(['gpg', '--import', private_key_path], gnupg_temp_home)
        if import_result.returncode != 0:
            print("[ERROR] ไม่สามารถ import private key ได้:", import_result.stderr)
            return None

        # Save message
        temp_input = os.path.join(gnupg_temp_home, "input.txt")
        signed_output = os.path.join(gnupg_temp_home, "signed.asc")
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(message_text)

        # Sign message
        sign_result = run_command([
            'gpg', '--clearsign',
            '--output', signed_output,
            temp_input
        ], gnupg_temp_home)

        if sign_result.returncode == 0:
            print("[SUCCESS] ลงลายเซ็นเรียบร้อย")
            with open(signed_output, encoding='utf-8') as f:
                print("\n[OUTPUT] ลายเซ็นที่ได้:\n")
                print(f.read())
            # copy signed.asc ไปไว้ที่ path ปัจจุบันของโปรแกรม
            output_copy = os.path.abspath("signed.asc")
            shutil.copyfile(signed_output, output_copy)
            print(f"[INFO] บันทึกไฟล์ลายเซ็นที่: {output_copy}")
            return output_copy
        else:
            print("[ERROR] ล้มเหลวในการลงลายเซ็น:", sign_result.stderr)
            return None


def gpg_verify_with_keyfile(signed_file_path, public_key_path):
    with tempfile.TemporaryDirectory() as gnupg_temp_home:
        print(f"📁 Temporary GNUPGHOME: {gnupg_temp_home}")

        # 1. Import public key
        import_result = run_command(['gpg', '--import', public_key_path], gnupg_temp_home)
        if import_result.returncode != 0:
            print("❌ ไม่สามารถ import public key ได้:", import_result.stderr)
            return

        # 2. Verify
        verify_result = run_command(['gpg', '--verify', signed_file_path], gnupg_temp_home)
        if verify_result.returncode == 0:
            print("✅ ลายเซ็นถูกต้อง")
        else:
            print("❌ ลายเซ็นไม่ถูกต้องหรือไม่รู้จัก public key:", verify_result.stderr)

# === MAIN ===
if __name__ == '__main__':
    # 🔑 ไฟล์คีย์ (คุณสามารถเปลี่ยน path ได้)
    private_key_file = r"C:\Users\65011\Desktop\Segano\work00002\key\private_key_C75DD9D5.asc"
    public_key_file = r"C:\Users\65011\Desktop\Segano\work00002\key\public_key_C75DD9D5.asc"

    # 🔏 ข้อความที่ต้องการเซ็น
    text = "สวัสดี! ข้อความนี้จะถูกลงลายเซ็นด้วย private key ที่อยู่ในไฟล์."

    # === ลงลายเซ็นข้อความ ===
    gpg_sign_with_keyfile(text, private_key_file)

    # === ตรวจสอบลายเซ็นที่ได้ ===
    signed_path = gpg_sign_with_keyfile(text, private_key_file)
    if signed_path:
        gpg_verify_with_keyfile(signed_path, public_key_file)
