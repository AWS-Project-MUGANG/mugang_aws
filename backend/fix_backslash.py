with open("main.py", encoding="utf-8") as f:
    content = f.read()

# 1451번째 줄의 잘못된 \\ 를 \ 로 교체
# "models.Depart.dept_no)\\\n" -> "models.Depart.dept_no)\\\n" 에서
# 실제로는 ".join(...)\\\\\n" 이 ".join(...)\\\n" 이 되어야 함

bad = 'models.Lecture.dept_no == models.Depart.dept_no)\\\\\n'
good = 'models.Lecture.dept_no == models.Depart.dept_no)\\\n'

if bad in content:
    content = content.replace(bad, good, 1)
    print("교체 성공!")
else:
    # 혹시 \r\n 버전인지 확인
    bad_rn = 'models.Lecture.dept_no == models.Depart.dept_no)\\\\\r\n'
    good_rn = 'models.Lecture.dept_no == models.Depart.dept_no)\\\r\n'
    if bad_rn in content:
        content = content.replace(bad_rn, good_rn, 1)
        print("교체 성공 (CRLF 버전)!")
    else:
        print("패턴을 찾지 못했습니다. 수동 확인 필요")
        # 해당 줄 찾아서 raw 출력
        for i, line in enumerate(content.split('\n')):
            if 'dept_no == models.Depart.dept_no)' in line:
                print(f"  Line {i+1}: {repr(line)}")
        import sys
        sys.exit(1)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("파일 저장 완료")
