import bcrypt

print("bcrypt version:", bcrypt.__version__)
try:
    hashed = bcrypt.hashpw(b"bintang123", bcrypt.gensalt())
    print("Success:", hashed)
except Exception as e:
    print("Error bcrypt:", e)

import passlib
print("passlib version:", passlib.__version__)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    hashed = pwd_context.hash("bintang123")
    print("Success passlib:", hashed)
except Exception as e:
    print("Error passlib:", e)
