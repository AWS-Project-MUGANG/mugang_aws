# Docker 실행 가이드

## 기본: 로컬 PostgreSQL 모드
`docker-compose.yml`은 로컬 DB 기준입니다.

```powershell
docker compose up --build
```

접속:
- Frontend: http://localhost:8888
- Backend health: http://localhost:8000/api/health

종료:
```powershell
docker compose down
```

## AWS 터널 모드(잔재 보관)
AWS Bastion + RDS 터널이 필요할 때만 아래 파일을 사용합니다.

```powershell
docker compose -f docker-compose.aws.yml up --build
```

종료:
```powershell
docker compose -f docker-compose.aws.yml down
```

## 참고
- 로컬 모드 DB 계정: `mugang / mugang`
- 로컬 모드 DB URL: `postgresql://mugang:mugang@db:5432/mugang`
