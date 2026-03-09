"""
DB의 role 값 소문자 → 대문자 마이그레이션
add_role_col.py 가 DEFAULT 'student'(소문자)로 컬럼을 추가해
기존 계정이 소문자 role을 갖는 문제를 수정합니다.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine

def fix_roles():
    with engine.begin() as conn:
        # 현재 상태 확인
        rows = conn.execute(text("SELECT loginid, user_name, role::text FROM user_tb ORDER BY role::text")).fetchall()
        print("\n[현재 사용자 목록]")
        for row in rows:
            print(f"  {row[0]:<20} {row[1]:<15} role={row[2]}")

        # role_enum이 허용하는 값 확인
        enum_vals = conn.execute(text(
            "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'role_enum'"
        )).fetchall()
        print(f"\n[role_enum 허용값]: {[v[0] for v in enum_vals]}")

        # role이 없거나 잘못된 계정 → STAFF로 강제 업데이트 (loginid로 직접 지정)
        r = conn.execute(text(
            "UPDATE user_tb SET role = 'STAFF'::role_enum WHERE loginid = 'Admin-0012' AND role::text != 'STAFF'"
        ))
        print(f"\nAdmin-0012 STAFF 업데이트: {r.rowcount}건")

if __name__ == "__main__":
    fix_roles()
