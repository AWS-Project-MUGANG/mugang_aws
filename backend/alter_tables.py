from database import engine
from sqlalchemy import text
import traceback

def add_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE user_tb ADD COLUMN IF NOT EXISTS email VARCHAR(150) UNIQUE;"))
            conn.execute(text("ALTER TABLE user_tb ADD COLUMN IF NOT EXISTS phone VARCHAR(20);"))
            conn.execute(text("ALTER TABLE user_tb ADD COLUMN IF NOT EXISTS is_first_login BOOLEAN DEFAULT TRUE;"))
            
            conn.execute(text("ALTER TABLE lecture_tb ADD COLUMN IF NOT EXISTS waitlist_capacity INTEGER DEFAULT 10;"))
            conn.execute(text("ALTER TABLE lecture_tb ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;"))
            conn.execute(text("ALTER TABLE lecture_tb ADD COLUMN IF NOT EXISTS classroom VARCHAR(100);"))
            
            conn.commit()
            print("Successfully added all required columns to PostgreSQL.")
        except Exception as e:
            print(f"Error occurred:")
            traceback.print_exc()

if __name__ == "__main__":
    add_columns()
