import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

# DB 연동
from database import engine, get_db, Base
import models

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 임시로 시작 시 DB 테이블 모두 자동 생성 (개발용)
models.Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="무강대학교 AI 학사행정 서비스",
    description="학생 맞춤형 학사 서비스 (수강신청, 시간표, RAG 기반 질의응답)",
    version="1.0.0"
)

# CORS 미들웨어 적용 (프론트엔드 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 개발 환경에서는 모두 허용, 운영 환경에서는 프론트 도메인만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Dummy Data Models ----
class LoginRequest(BaseModel):
    student_id: str
    password: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class FormRequest(BaseModel):
    form_type: str
    reason: str

class EnrollmentRequest(BaseModel):
    user_id: str
    subject: str
    college: str
    department: str
    room: str

# ---- API 라우터 (뼈대) ----

@app.get("/")
def read_root():
    return {"message": "무강대학교 AI 학사행정 API 서버가 실행 중입니다."}

@app.post("/api/v1/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    학생 학번(사번)을 통한 로그인 처리 및 DB 유저 생성(없을 경우)
    """
    logger.info(f"로그인 시도: {req.student_id}")
    if req.student_id and req.password:
        # 간단한 자동 회원가입 로직 (실무에서는 회원가입/비번대조 분리 필요)
        user = db.query(models.User).filter(models.User.student_id == req.student_id).first()
        if not user:
            user = models.User(
                student_id=req.student_id,
                password_hash="hashed_dummy",
                name=req.student_id + " 님",
                major="테스트학과"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return {"access_token": "fake_jwt_token_12345", "user_id": user.id, "role": "admin" if "admin" in req.student_id.lower() or "prof" in req.student_id.lower() else "student"}
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

@app.post("/api/v1/chat/ask")
def chat_ask(req: ChatRequest):
    """
    AI 학사 행정 상담 (RAG 기반 응답 로직 연결부)
    """
    # TODO: Pinecone / LLM(Bedrock 등) 연결 후 답변 생성 로직 연동
    logger.info(f"채팅 질의 수신 - session: {req.session_id}, msg: {req.message}")
    return {
        "reply": f"네, 질문하신 내용 '{req.message}'에 대해 확인 중입니다. (RAG 연동 전 기본 응답)",
        "sources": [{"title": "학칙 임시", "url": "#"}]
    }

@app.get("/api/v1/enrollments/{user_id}")
def get_user_enrollments(user_id: str, db: Session = Depends(get_db)):
    """
    사용자의 수강신청 내역 조회
    """
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.user_id == user_id).all()
    # Pydantic 응답 모델없이 직접 딕셔너리로 변환
    result = []
    for en in enrollments:
        result.append({
            "id": en.id,
            "subject": en.subject,
            "college": en.college,
            "department": en.department,
            "room": en.room,
            "created_at": en.created_at.isoformat()
        })
    return {"schedules": result}

@app.post("/api/v1/enrollments")
def create_enrollment(req: EnrollmentRequest, db: Session = Depends(get_db)):
    """
    학생 수강신청 건 1개 저장
    """
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

    new_enrollment = models.Enrollment(
        user_id=req.user_id,
        subject=req.subject,
        college=req.college,
        department=req.department,
        room=req.room
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return {"message": "정상적으로 수강신청 테이블에 저장되었습니다.", "enrollment_id": new_enrollment.id}

@app.post("/api/v1/forms/generate")
def generate_form(req: FormRequest):
    """
    문서 초안 자동 생성 (휴학 등)
    """
    # TODO: AI 문서 자동 완성 기능 연동
    return {
        "form_id": "draft_001",
        "status": "draft",
        "preview_json": {"applicant": "test", "reason": req.reason}
    }

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    pass
