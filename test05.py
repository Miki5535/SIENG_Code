import gnupg
from pathlib import Path
import os
import datetime

# กำหนด path สำหรับ gnupghome
gnupg_home = Path.home() / ".gnupg"

# ตรวจสอบและสร้างโฟลเดอร์หากไม่มี
if not gnupg_home.exists():
    os.makedirs(gnupg_home)

# สร้าง GPG object
gpg = gnupg.GPG(gnupghome=str(gnupg_home))

# สร้าง Key Pair
def generate_key():
    print("Generating a new GPG key pair...")
    input_data = gpg.gen_key_input(
        name_email="your_email@example.com",
        name_real="Your Name",
        passphrase="your_passphrase",  # ตั้งรหัสผ่านสำหรับ private key
        key_type="RSA",
        key_length=2048,
        expire_date="1y",  # ระบุว่า Key จะหมดอายุใน 1 ปี (สามารถตั้งค่าเช่น '1w', '1m', '2y' ได้)
    )
    key = gpg.gen_key(input_data)
    fingerprint = key.fingerprint
    print(f"Key created: {fingerprint}")
    return fingerprint

# แสดงข้อมูลคีย์ทั้งหมดในระบบ
def list_all_keys():
    public_keys = gpg.list_keys()
    if public_keys:
        print("Available public keys:\n" + "-" * 40)  # Print a separator line
        for key in public_keys:
            # Convert the creation timestamp to datetime
            creation_timestamp = int(key['date'])
            creation_date = datetime.datetime.fromtimestamp(creation_timestamp, datetime.timezone.utc)
            
            # Check if the key has an expiration date and convert it
            if 'expires' in key:
                expiration_timestamp = int(key['expires'])
                expiration_date = datetime.datetime.fromtimestamp(expiration_timestamp, datetime.timezone.utc)
                expiration_date_str = expiration_date.strftime("%Y-%m-%d")
                
                # Calculate days remaining until expiration
                days_remaining = (expiration_date - datetime.datetime.now(datetime.timezone.utc)).days
            else:
                expiration_date_str = "No expiration"
                days_remaining = None  # No expiration
            
            # Print the key's details in a clear format
            print(f"\nFingerprint: {key['fingerprint']}")
            print(f"User: {', '.join(key['uids'])}")
            print(f"Creation Date: {creation_date.strftime('%Y-%m-%d')}")
            print(f"Expiration Date: {expiration_date_str}")
            
            # Display the number of days remaining if the key has an expiration date
            if days_remaining is not None:
                if days_remaining > 0:
                    print(f"Days Remaining: {days_remaining} days")
                elif days_remaining == 0:
                    print(f"Days Remaining: Expiring today!")
                else:
                    print(f"Days Remaining: Expired {abs(days_remaining)} days ago")
            
            print("-" * 40)  # Print a separator line between keys
    else:
        print("No public keys found.")


# ดึง Public และ Private Key
def export_keys(fingerprint):
    # Export Public Key
    public_key = gpg.export_keys(fingerprint)
    with open("public_key.asc", "w") as pub_file:
        pub_file.write(public_key)
    print("Public key saved as 'public_key.asc'")

    # Export Private Key (ต้องระบุ passphrase)
    private_key = gpg.export_keys(fingerprint, secret=True, passphrase="your_passphrase")
    with open("private_key.asc", "w") as priv_file:
        priv_file.write(private_key)
    print("Private key saved as 'private_key.asc'")

# สร้างคีย์ใหม่ที่มีอายุการใช้งานยาวนานขึ้น
def create_key_with_extended_expiration(expiration="2y"):
    print(f"Creating a new key with {expiration} expiration...")
    input_data = gpg.gen_key_input(
        name_email="hdsd45465646@example.com",
        name_real="mikkee",
        passphrase="your_passphrase",  # ตั้งรหัสผ่านสำหรับ private key
        key_type="RSA",
        key_length=2048,
        expire_date=expiration,  # ระบุอายุใหม่ตั้งแต่ต้น
    )
    key = gpg.gen_key(input_data)
    print(f"New key created with {expiration} expiration: {key.fingerprint}")
    return key.fingerprint

# ลบคีย์
def delete_key(fingerprint, passphrase):
    print(f"Deleting key with fingerprint: {fingerprint}")
    # ลบทั้ง public และ private key
    gpg.delete_keys(fingerprint)
    gpg.delete_keys(fingerprint, secret=True, passphrase=passphrase)
    print(f"Key with fingerprint {fingerprint} deleted.")

# ลบคีย์ทั้งหมด
def delete_all_keys():
    public_keys = gpg.list_keys()
    private_keys = gpg.list_keys(secret=True)
    
    

    if public_keys:
        for key in public_keys:
            delete_key(key['fingerprint'],"your_passphrase")
            # print(f"Fingerprint: {key['fingerprint']}, User: {key['uids']}")
        print("All keys have been deleted.")
    else:
        print("No public keys found.")



    


# อัปเดตคีย์ (เช่น การเปลี่ยนอายุการหมดอายุ)
def update_key_expiration(fingerprint, new_expiration="2y"):
    print(f"Updating key expiration for key with fingerprint: {fingerprint}")
    # ใช้คำสั่ง gpg --edit-key เพื่อปรับปรุง expiration
    gpg.edit_key(fingerprint)
    gpg.set_key_expiration(fingerprint, new_expiration)
    gpg.save_key(fingerprint)
    print(f"Expiration updated to {new_expiration} for key with fingerprint {fingerprint}")

# เริ่มกระบวนการ
if __name__ == "__main__":
    print("=== GPG Key Generation and Management ===")
    
    # ให้ผู้ใช้เลือกการดำเนินการ
    print("What would you like to do?")
    print("1. Create a new key with 1 year expiration (original)")
    print("2. Create a new key with custom expiration")
    print("3. Delete a key")
    print("4. Update key expiration")
    print("5. Delete all keys")
    print("6. list")

    choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

    
    if choice == "2":
        expiration = input("Enter expiration (e.g., 2y, 5y, 10y): ")
        fingerprint = create_key_with_extended_expiration(expiration)
    elif choice == "1":
        # สร้างคีย์คู่ตามค่าเริ่มต้น (1 ปี)
        fingerprint = generate_key()
    elif choice == "3":
        # Example usage
        fingerprint = input("Enter the fingerprint of the key to delete: ")
        passphrase = input("Enter the passphrase for the key: ")  # รับรหัสผ่านจากผู้ใช้
        delete_key(fingerprint, passphrase)

    elif choice == "4":
        fingerprint = input("Enter the fingerprint of the key to update: ")
        new_expiration = input("Enter new expiration (e.g., 2y, 5y): ")
        update_key_expiration(fingerprint, new_expiration)
    elif choice == "5":
        delete_all_keys()
    elif choice == "6":
        list_all_keys()

    

