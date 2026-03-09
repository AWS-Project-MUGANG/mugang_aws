"""
lecture_tb.csv, schedule_tb.csv 를 DB에 저장하는 스크립트

실행: python csvtoDB.py
"""

import csv
import os
from sqlalchemy import text
from database import engine
import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LECTURE_CSV = os.path.join(BASE_DIR, "lecture_tb.csv")
SCHEDULE_CSV = os.path.join(BASE_DIR, "schedule_tb.csv")

IS_POSTGRES = "postgresql" in str(engine.url)


def to_mins(t_str: str) -> int:
    """'HH:MM:SS' 또는 'HH:MM' 문자열을 분으로 변환"""
    parts = t_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def load_dept_map(conn) -> dict:
    """depart_tb 전체 로드 → {depart명: dept_no} 딕셔너리 반환"""
    rows = conn.execute(text("SELECT dept_no, depart FROM depart_tb")).fetchall()
    return {depart: dept_no for dept_no, depart in rows}


def resolve_dept_no(department: str, dept_map: dict) -> int | None:
    """
    lecture.department(약칭) → dept_no 변환.
    - 정확히 1개의 depart_tb 항목에만 포함될 때만 매핑.
    - 0개(매핑 불가) 또는 2개 이상(모호)이면 NULL 반환.
    """
    hits = [dept_no for depart, dept_no in dept_map.items() if department in depart]
    return hits[0] if len(hits) == 1 else None


def insert_lectures(conn) -> dict:
    """lecture_tb.csv → lecture_tb 삽입. course_no -> lecture_id 매핑 반환"""
    dept_map = load_dept_map(conn)
    course_to_id = {}
    inserted = skipped = dept_mapped = 0

    with open(LECTURE_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            existing = conn.execute(
                text("SELECT lecture_id FROM lecture_tb WHERE course_no = :cn"),
                {"cn": row["course_no"]},
            ).fetchone()

            if existing:
                course_to_id[row["course_no"]] = existing[0]
                skipped += 1
                continue

            dept_no = resolve_dept_no(row["department"], dept_map)
            if dept_no:
                dept_mapped += 1

            params = _lecture_params(row, dept_no)

            if IS_POSTGRES:
                result = conn.execute(
                    text("""
                        INSERT INTO lecture_tb
                            (course_no, subject, department, dept_no, lec_grade, credit,
                             professor, type, capacity, count, version, waitlist_capacity)
                        VALUES
                            (:course_no, :subject, :department, :dept_no, :lec_grade, :credit,
                             :professor, CAST(:ltype AS lecture_category), :capacity, :count, :version, :waitlist_capacity)
                        RETURNING lecture_id
                    """),
                    params,
                )
                lecture_id = result.fetchone()[0]
            else:
                conn.execute(
                    text("""
                        INSERT INTO lecture_tb
                            (course_no, subject, department, dept_no, lec_grade, credit,
                             professor, type, capacity, count, version, waitlist_capacity)
                        VALUES
                            (:course_no, :subject, :department, :dept_no, :lec_grade, :credit,
                             :professor, :type, :capacity, :count, :version, :waitlist_capacity)
                    """),
                    params,
                )
                lecture_id = conn.execute(
                    text("SELECT lecture_id FROM lecture_tb WHERE course_no = :cn"),
                    {"cn": row["course_no"]},
                ).fetchone()[0]

            course_to_id[row["course_no"]] = lecture_id
            inserted += 1

    conn.commit()
    print(f"  lecture_tb: {inserted}건 삽입 (dept_no 매핑: {dept_mapped}건, NULL: {inserted - dept_mapped}건), {skipped}건 스킵")
    return course_to_id


_TYPE_MAP = {
    "MAJOR_REQUIRED":   "전공필수",
    "MAJOR_ELECTIVE":   "전공선택",
    "LIBERAL_REQUIRED": "교양필수",
    "LIBERAL_ELECTIVE": "교양선택",
    "TEACHING":         "교직",
    "COMMON":           "공통",
}


def _lecture_params(row: dict, dept_no: int | None) -> dict:
    return {
        "course_no": row["course_no"],
        "subject": row["subject"],
        "department": row["department"],
        "dept_no": dept_no,
        "lec_grade": row["lec_grade"],
        "credit": int(row["credit"]),
        "professor": row["professor"],
        "ltype": _TYPE_MAP.get(row["type"], "전공선택"),
        "capacity": int(row["capacity"]),
        "count": int(row["count"]),
        "version": int(row["version"]),
        "waitlist_capacity": int(row["waitlist_capacity"]),
    }


def insert_schedules(conn, course_to_id: dict) -> None:
    """schedule_tb.csv → schedule_tb 삽입"""
    inserted = skipped = 0

    with open(SCHEDULE_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            lecture_id = course_to_id.get(row["course_no"])
            if lecture_id is None:
                print(f"  경고: course_no={row['course_no']} 강의 없음, 스킵")
                skipped += 1
                continue

            start_time = row["start_time"]
            end_time = row["end_time"]

            if IS_POSTGRES:
                conn.execute(
                    text("""
                        INSERT INTO schedule_tb
                            (lecture_id, day_of_week, start_time, end_time, start_min, end_min, classroom)
                        VALUES
                            (:lecture_id, :day_of_week, CAST(:start_time AS time), CAST(:end_time AS time), :start_min, :end_min, :classroom)
                    """),
                    _schedule_params(lecture_id, row, start_time, end_time),
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO schedule_tb
                            (lecture_id, day_of_week, start_time, end_time, start_min, end_min, classroom)
                        VALUES
                            (:lecture_id, :day_of_week, :start_time, :end_time, :start_min, :end_min, :classroom)
                    """),
                    _schedule_params(lecture_id, row, start_time, end_time),
                )
            inserted += 1

    conn.commit()
    print(f"  schedule_tb: {inserted}건 삽입, {skipped}건 스킵")


def _schedule_params(lecture_id: int, row: dict, start_time: str, end_time: str) -> dict:
    return {
        "lecture_id": lecture_id,
        "day_of_week": row["day_of_week"],
        "start_time": start_time,
        "end_time": end_time,
        "start_min": to_mins(start_time),
        "end_min": to_mins(end_time),
        "classroom": row.get("classroom", ""),
    }


def main():
    models.Base.metadata.create_all(bind=engine)
    db_type = "PostgreSQL" if IS_POSTGRES else "SQLite"
    print(f"DB 연결: {db_type}")

    with engine.connect() as conn:
        print("\n[1/2] lecture_tb.csv 저장 중...")
        course_to_id = insert_lectures(conn)

        print("\n[2/2] schedule_tb.csv 저장 중...")
        insert_schedules(conn, course_to_id)

    print("\n완료.")


if __name__ == "__main__":
    main()
