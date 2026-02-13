from auth import get_password_hash, verify_password

try:
    password = "securepassword123"
    print(f"Hashing password: {password}")
    hashed = get_password_hash(password)
    print(f"Hashed: {hashed}")
    
    print("Verifying password...")
    is_valid = verify_password(password, hashed)
    print(f"Is valid: {is_valid}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
