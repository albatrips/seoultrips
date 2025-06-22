from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os, shutil
from random import choice

# 라우터 및 템플릿 설정
router = APIRouter()
templates = Jinja2Templates(directory="server/templates")
UPLOAD_DIR = "server/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 추천 퀘스트 생성 (임시 하드코딩)
@router.post("/recommend")
async def recommend(request: Request, theme: str = Form(...)):
    steps = [
        {
            "id": 1,
            "title": "경복궁 방문",
            "lat": 37.579617,
            "lng": 126.977041,
            "description": f"'{theme}' 테마로 경복궁을 방문하세요."
        }
    ]
    request.app.state.current_quests = steps
    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": theme,
        "steps": steps
    })

# 퀘스트 상세 페이지 렌더링
@router.get("/quest/{quest_id}")
async def quest_detail(request: Request, quest_id: int, result: str = ""):
    quests = getattr(request.app.state, "current_quests", [])
    quest = next((q for q in quests if q["id"] == quest_id), {
        "id": quest_id,
        "title": "예시 퀘스트",
        "lat": 37.579617,
        "lng": 126.977041,
        "description": "예시 퀘스트입니다."
    })
    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest,
        "result": result
    })

# 사진 업로드 처리 후 퀘스트 결과 표시
@router.post("/upload-photo")
async def upload_photo(request: Request, photo: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, photo.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    result = choice(["success", "fail"])  # 임의 판단

    # 현재 퀘스트 상태를 사용해 quest 정보 가져오기
    quests = getattr(request.app.state, "current_quests", [])
    quest = quests[0] if quests else {
        "id": 1,
        "title": "경복궁 방문",
        "lat": 37.579617,
        "lng": 126.977041,
        "description": "경복궁에 방문하세요."
    }

    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest,
        "result": result,
        "uploaded_photo": f"/static/uploads/{photo.filename}"
    })
