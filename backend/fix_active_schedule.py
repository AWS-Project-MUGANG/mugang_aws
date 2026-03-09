with open("main.py", "rb") as f:
    raw = f.read()

content = raw.decode("utf-8", errors="replace")

# 교체할 대상 (168번째 줄 시작부터 209번째 줄 끝까지, 즉 망가진 블록 전체)
old_block_start = 'def _get_active_schedule(db: Session):\r\n    """현재 시각에 해당하는 EnrollmentSchedule 반환 (없으면 None)"""\r\n    # DB의 DateTime은 UTC naive로 저장되므로, naive UTC datetime과 비교합니다.\r\n    now = datetime.now(timezone.utc)'

# 찾아서 끝까지 (다음 최상위 함수/클래스까지) 교체
start_idx = content.find('def _get_active_schedule(db: Session):')
if start_idx == -1:
    print("ERROR: 시작점을 찾지 못했습니다!")
    exit(1)

# 209번째 줄 이후인 "\r\n\r\n\r\n# ---- API 라우터" 또는 "\r\ndef " 탑레벨 찾기
# 문자열에서 209번째 줄 끝 이후를 찾아야 함
# 실제로는 "return {\"allowed\": True, \"reason\": \"허용\", \"active_day\": active.day_n" 이후의 \r\n\r\n\r\n

# 현실적으로: start_idx 이후에 나오는 "\r\n\r\n\r\n" (빈줄 두개) 찾기
end_idx = content.find('\r\n\r\n\r\n# ---- API', start_idx)
if end_idx == -1:
    end_idx = content.find('\r\n\r\n\r\n', start_idx)

print(f"start_idx={start_idx}, end_idx={end_idx}")
print("교체 대상 끝 부근:")
print(repr(content[end_idx:end_idx+100]))

# 새 함수
new_func = '''def _get_active_schedule(db: Session):
    """현재 시각에 해당하는 EnrollmentSchedule 반환 (없으면 None)"""
    # DB의 DateTime은 UTC naive로 저장되므로, naive UTC datetime과 비교합니다.
    now = datetime.utcnow()
    return db.query(models.EnrollmentSchedule).filter(
        models.EnrollmentSchedule.is_active == True,
        models.EnrollmentSchedule.open_datetime <= now,
        models.EnrollmentSchedule.close_datetime >= now
    ).first()'''

new_content = content[:start_idx] + new_func + content[end_idx:]

with open("main.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("SUCCESS!")
