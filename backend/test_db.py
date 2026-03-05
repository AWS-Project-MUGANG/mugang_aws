from database import SessionLocal
import models
import traceback

db = SessionLocal()
try:
    user = db.query(models.User).filter(models.User.loginid == "22517717").first()
    print("User found:", user)
except Exception as e:
    with open("test_err.txt", "w") as f:
        f.write(traceback.format_exc())
