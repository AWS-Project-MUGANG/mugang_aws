from database import engine
from sqlalchemy import text

def create_indexes():
    queries = [
        "CREATE INDEX IF NOT EXISTS idx_enroll_status ON enroll_tb (enroll_status);",
        "CREATE INDEX IF NOT EXISTS idx_waitlist_status ON waitlist_tb (status);",
        "CREATE INDEX IF NOT EXISTS idx_user_role ON user_tb (role);",
        "CREATE INDEX IF NOT EXISTS idx_waitlist_created ON waitlist_tb (createdat);"
    ]
    with engine.connect() as conn:
        for q in queries:
            try:
                conn.execute(text(q))
                print(f"Executed: {q}")
            except Exception as e:
                print(f"Failed: {q} - {e}")
        conn.commit()

if __name__ == "__main__":
    create_indexes()
