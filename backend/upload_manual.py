# upload_manual.py (생성 후 실행)
import requests
import os

# 1. 서버 주소 확인 (로컬 테스트 시 localhost:8000)
url = "http://localhost:8000/api/v1/admin/rag/upload"

# 2. 업로드할 파일 경로 (스크립트와 같은 폴더에 pdf가 있거나 절대 경로 입력)
# 예: 같은 폴더에 2026_student_menual.pdf 파일이 있어야 함
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_dir, "pdf", "2026_student_menual.pdf")

if not os.path.exists(file_path):
    # 테스트를 위한 더미 파일 생성 (파일이 없을 경우)
    print(f"⚠️ '{file_path}' 파일이 없습니다. (현재 실행 위치: {os.getcwd()})\n테스트용 텍스트 파일로 대체합니다.")
    file_path = "test_manual.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("2026학년도 수강신청 기간은 2월 10일부터 2월 14일까지입니다.\n졸업 요건은 전공 60학점, 교양 30학점 포함 총 130학점입니다.")

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"title": "2026 학생 학사 매뉴얼"}
        print(f"📤 문서 업로드 중... ({file_path})")
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            print("✅ 업로드 성공:", response.json())
        else:
            print(f"❌ 업로드 실패 (Status {response.status_code}):", response.text)

except Exception as e:
    print(f"❌ 오류 발생: {e}")
