from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os, shutil
from random import choice

router = APIRouter()
templates = Jinja2Templates(directory="server/templates")
UPLOAD_DIR = "server/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ 추천 퀘스트
@router.post("/recommend")
async def recommend(request: Request, theme: str = Form(...)):
    steps = [
        {
            "id": 1,
            "title": "경복궁 방문",
            "lat": 37.579617,
            "lng": 126.977041,
            "description": f"{theme} 테마로 경복궁을 방문하세요."
        },
        {
            "id": 2,
            "title": "북촌한옥마을 산책",
            "lat": 37.582604,
            "lng": 126.983998,
            "description": f"{theme} 테마로 북촌한옥마을을 산책하세요."
        },
        {
            "id": 3,
            "title": "청계천 산책",
            "lat": 37.570377,
            "lng": 126.978104,
            "description": f"{theme} 테마로 청계천을 걸어보세요."
        }
    ]
    request.app.state.current_quests = steps
    return templates.TemplateResponse("recommend.html", {
        "request": request,
        "theme": theme,
        "steps": steps
    })

# ✅ 퀘스트 목록 페이지
@router.get("/quest")
async def quest_course(request: Request):
    steps = getattr(request.app.state, "current_quests", [])
    if not steps:
        steps = [
            {
                "id": 1,
                "title": "경복궁 방문",
                "lat": 37.579617,
                "lng": 126.977041,
                "description": "경복궁을 방문하세요."
            },
            {
                "id": 2,
                "title": "북촌한옥마을 산책",
                "lat": 37.582604,
                "lng": 126.983998,
                "description": "북촌한옥마을을 산책하세요."
            },
            {
                "id": 3,
                "title": "청계천 산책",
                "lat": 37.570377,
                "lng": 126.978104,
                "description": "청계천을 걸어보세요."
            }
        ]
        request.app.state.current_quests = steps

    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": "기본",
        "steps": steps
    })

# ✅ 퀘스트 상세 페이지
@router.get("/quest/{quest_id}")
async def quest_detail(request: Request, quest_id: int, result: str = "", theme: str = "기본"):
    quests = getattr(request.app.state, "current_quests", [])
    quest = next((q for q in quests if q["id"] == quest_id), {
        "id": quest_id,
        "title": "예시 퀘스트",
        "lat": 0.0,
        "lng": 0.0,
        "description": "예시 퀘스트입니다."
    })
    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest,
        "result": result,
        "theme": theme
    })

# ✅ 사진 업로드 및 성공/실패 판단
@router.post("/upload-photo")
async def upload_photo(
    request: Request,
    photo: UploadFile = File(...),
    quest_id: int = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, photo.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    result = choice(["success", "fail"])
    quests = getattr(request.app.state, "current_quests", [])
    quest = next((q for q in quests if q["id"] == quest_id), {
        "id": quest_id,
        "title": "퀘스트",
        "lat": 0.0,
        "lng": 0.0,
        "description": "기본 퀘스트입니다."
    })

    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest,
        "result": result,
        "uploaded_photo": f"/static/uploads/{photo.filename}"
    })

# ✅ 사용자 정의 퀘스트 입력 페이지
@router.get("/custom")
async def custom_input(request: Request):
    return templates.TemplateResponse("custom.html", {"request": request})

# ✅ 사용자 정의 퀘스트 제출
@router.post("/custom-submit")
async def custom_submit(
    request: Request,
    title: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...)
):
    custom_step = {
        "id": 999,
        "title": title,
        "lat": lat,
        "lng": lng,
        "description": "사용자 지정 퀘스트입니다."
    }
    request.app.state.current_quests = [custom_step]
    return RedirectResponse(url="/api/quest", status_code=302)

