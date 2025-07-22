import gnupg

# สร้าง instance ของ GPG
gpg = gnupg.GPG()

# 1. สร้างคู่กุญแจ RSA
input_data = gpg.gen_key_input(
    name_email='alice@example.com',
    name_real='Alice',
    passphrase='mysecretpassphrase',
    key_type='RSA',
    key_length=2048,
)
key = gpg.gen_key(input_data)

# 2. เซ็นข้อความโดยใช้ private key
message = "This is a message to be signed."
signed_data = gpg.sign(message, keyid=key.fingerprint, passphrase='mysecretpassphrase')

print("Signed Data:\n", signed_data)

# 3. บันทึกลายเซ็นไว้ในไฟล์
with open('signed_message.asc', 'w') as f:
    f.write(str(signed_data))

# 4. นำ public key ไปให้ผู้รับเพื่อตรวจสอบ
public_key = gpg.export_keys(key.fingerprint)
with open('public_key.asc', 'w') as f:
    f.write(public_key)

# 5. ฝั่งผู้รับ: นำเข้า public key และตรวจสอบลายเซ็น
gpg_import = gnupg.GPG()
gpg_import.import_keys(public_key)

with open('signed_message.asc') as f:
    verification = gpg_import.verify_file(f)

if verification:
    print("✅ ลายเซ็นถูกต้อง")
else:
    print("❌ ลายเซ็นไม่ถูกต้องหรือข้อมูลถูกเปลี่ยนแปลง")