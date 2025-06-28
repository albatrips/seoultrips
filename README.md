# 🎮 SeoulTrips - AI 기반 서울 퀘스트 여행 플랫폼

서울의 숨겨진 보물을 찾아 떠나는 특별한 여정! AI가 생성하는 맞춤형 퀘스트로 서울을 새롭게 탐험해보세요.

## ✨ 주요 기능

### 🎯 퀘스트 시스템

- **AI 퀘스트 생성**: 사용자 맞춤형 서울 탐험 퀘스트 자동 생성
- **테마별 추천**: 카테고리 기반 추천 루트 제공
- **실시간 진행률**: 퀘스트 완료 상태 실시간 추적
- **지역별 탐험**: 서울 25개 자치구별 맞춤 퀘스트

### 🗺️ 인터랙티브 맵

- **네이버 지도 연동**: 실제 위치 기반 퀘스트 진행
- **마커 시스템**: 퀘스트 위치 시각화 및 상태 표시
- **경로 안내**: 퀘스트 간 자연스러운 이동 경로 제공

### 📸 미션 시스템

- **포토 미션**: 특정 장소에서의 인증샷 촬영
- **체험 미션**: 카페, 문화시설 등 다양한 액티비티
- **완료 인증**: 이미지 업로드를 통한 퀘스트 완료 확인

### 🎨 게임화된 UI/UX

- **픽셀 아트 스타일**: 게임 느낌의 독특한 디자인
- **애니메이션 효과**: 부드러운 전환과 시각적 피드백
- **반응형 디자인**: 모바일/데스크톱 최적화

## 🛠️ 기술 스택

### Backend

- **FastAPI**: 고성능 Python 웹 프레임워크
- **LangChain**: AI 언어모델 통합 프레임워크
- **MySQL**: 관계형 데이터베이스
- **OpenAI GPT**: AI 퀘스트 생성 엔진

### Frontend

- **HTML5/CSS3**: 웹 표준 기반 UI
- **JavaScript**: 인터랙티브 기능 구현
- **Naver Maps API**: 지도 서비스 연동
- **Jinja2**: 서버사이드 템플릿 엔진

### Infrastructure

- **Docker**: 컨테이너화된 배포
- **Docker Compose**: 멀티 컨테이너 오케스트레이션

## 🚀 빠른 시작

### 필수 요구사항

- Docker & Docker Compose
- OpenAI API Key (AI 퀘스트 생성용)
- Naver Maps API Key (지도 서비스용)

### 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음을 추가하세요:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Naver Maps API Configuration
NAVER_MAPS_CLIENT_ID=your_naver_maps_client_id

# Database Configuration (Docker Compose 사용시 기본값)
DB_HOST=db
DB_PORT=3306
DB_USER=user
DB_PASS=password
DB_NAME=albatrips
```

### Docker로 실행하기

1. **프로젝트 클론**

```bash
git clone https://github.com/albatrips/seoultrips.git
cd seoultrips
```

2. **Docker 이미지 빌드**

```bash
docker-compose build
```

3. **서비스 시작**

```bash
docker-compose up -d
```

4. **로그 확인**

```bash
# API 서버 로그 실시간 확인
docker-compose logs -f api

# 전체 서비스 로그 확인
docker-compose logs -f

# 데이터베이스 로그 확인
docker-compose logs -f db
```

5. **애플리케이션 접속**

- 웹 애플리케이션: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 로컬 개발 환경 설정

1. **Python 가상환경 설정**

```bash
# uv 사용 (권장)
uv init
uv venv --python 3.11
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 또는 기본 venv 사용
python -m venv .venv
source .venv/bin/activate
```

2. **의존성 설치**

```bash
# uv 사용
uv add -r requirements.txt

# 또는 pip 사용
pip install -r requirements.txt
```

3. **데이터베이스 설정**

```bash
# MySQL 서버만 Docker로 실행
docker-compose up -d db
```

4. **개발 서버 실행**

```bash
# 방법 1: uvicorn 직접 실행
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# 방법 2: main.py 실행
python main.py

# 방법 3: uv 사용
uv run server/app.py
```

## 📂 프로젝트 구조

```
seoultrips/
├── server/                     # 백엔드 소스코드
│   ├── api/                   # API 라우터
│   │   ├── quest.py          # 퀘스트 관련 API
│   │   ├── recommend.py      # 추천 시스템 API
│   │   ├── location.py       # 위치 서비스 API
│   │   └── image_upload.py   # 이미지 업로드 API
│   ├── services/             # 비즈니스 로직
│   │   ├── client.py         # 데이터베이스 클라이언트
│   │   ├── quest_generate.py # AI 퀘스트 생성
│   │   └── korea_tour_api.py # 한국관광공사 API 연동
│   ├── templates/            # HTML 템플릿
│   │   ├── initial.html      # 메인 페이지
│   │   ├── category.html     # 카테고리 선택
│   │   ├── recommend.html    # 추천 루트
│   │   ├── custom.html       # 커스텀 퀘스트 생성
│   │   └── quest_course.html # 퀘스트 진행
│   ├── static/               # 정적 파일
│   └── app.py               # FastAPI 애플리케이션
├── db/                       # 데이터베이스 설정
│   ├── Dockerfile           # MySQL Docker 설정
│   └── init/                # 초기 스키마/데이터
├── docker-compose.yml        # Docker Compose 설정
├── Dockerfile               # API 서버 Docker 설정
├── requirements.txt         # Python 의존성
├── main.py                  # 애플리케이션 진입점
└── README.md               # 프로젝트 문서
```

## 🎮 사용 방법

### 1. 사용자 등록

- 나이, 성별, 선호 지역, 여행 시간 설정

### 2. 퀘스트 선택

- **테마별 추천**: 미리 준비된 추천 루트 선택
- **커스텀 생성**: AI를 활용한 맞춤형 퀘스트 생성

### 3. 퀘스트 진행

- 지도에서 퀘스트 위치 확인
- 각 장소 방문 및 미션 수행
- 포토 미션 완료 및 인증

### 4. 진행률 추적

- 실시간 퀘스트 완료 현황 확인
- 경험치 바를 통한 시각적 피드백

## 🔧 개발 가이드

### 브랜치 전략

1. **절대 main 브랜치에서 직접 개발 금지**
2. **개별 feature 브랜치 생성**

```bash
git checkout -b feature/your-feature-name
```

3. **Pull Request를 통한 코드 리뷰 및 병합**

### 커밋 컨벤션

- 자유로운 커밋, 단 의미있는 단위로 구분
- 너무 세분화하지 말고 적절한 크기로 커밋

### 이슈 관리

- 문제 발견시 GitHub Issues 활용
- 기능 개선 제안도 Issues로 등록

## 🐳 Docker 명령어 모음

### 기본 명령어

```bash
# 전체 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d api
docker-compose up -d db

# 서비스 중지
docker-compose down

# 볼륨까지 삭제하며 중지
docker-compose down -v
```

### 로그 확인

```bash
# API 서버 로그 실시간 확인
docker-compose logs -f api

# 데이터베이스 로그 확인
docker-compose logs -f db

# 전체 로그 확인
docker-compose logs -f

# 마지막 100줄만 확인
docker-compose logs --tail=100 api
```

### 개발 중 유용한 명령어

```bash
# 이미지 재빌드
docker-compose build --no-cache

# 컨테이너 내부 접속
docker-compose exec api bash
docker-compose exec db mysql -u user -p

# 서비스 재시작
docker-compose restart api
```

## 🔍 트러블슈팅

### 포트 충돌 문제

```bash
# 8000 포트 사용 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 데이터베이스 연결 문제

```bash
# 데이터베이스 컨테이너 상태 확인
docker-compose ps db

# 데이터베이스 로그 확인
docker-compose logs db

# 데이터베이스 재시작
docker-compose restart db
```

### 의존성 문제

```bash
# 컨테이너 재빌드
docker-compose build --no-cache api

# 로컬 환경 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트 관련 문의나 버그 리포트는 GitHub Issues를 활용해주세요.

---

**Happy Questing! 🎮✨**
