from database import engine
from sqlalchemy import text
import traceback

def cleanup():
    with engine.connect() as conn:
        try:
            # Drop AI garbage tables completely
            conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS document_metadata CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS forms CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS grades CASCADE;"))
            
            # Since enrollments logic was moved to enroll_tb, drop enrollments table
            conn.execute(text("DROP TABLE IF EXISTS enrollments CASCADE;"))
            
            # Modify enroll_tb to handle AI logic (status)
            conn.execute(text("ALTER TABLE enroll_tb ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'cart';"))
            
            # Rename tables to fit _tb convention if they exist
            tables_to_rename = {
                'notices': 'notice_tb',
                'enrollment_schedule': 'enroll_schedule_tb',
                'system_configs': 'system_config_tb'
            }
            
            for old_name, new_name in tables_to_rename.items():
                try:
                    conn.execute(text(f"ALTER TABLE {old_name} RENAME TO {new_name};"))
                    print(f"Renamed {old_name} to {new_name}")
                except Exception as e:
                    # Might have been renamed already or missing
                    pass
            
            conn.commit()
            print("Successfully cleaned up database tables.")
        except Exception as e:
            print(f"Error occurred:")
            traceback.print_exc()

if __name__ == "__main__":
    cleanup()
