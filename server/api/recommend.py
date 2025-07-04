from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import os, shutil
from random import choice
from server.services.client import get_routes_by_categories, get_set_by_id, create_quests, get_all_quests, get_quest_by_id
import json

router = APIRouter()
templates = Jinja2Templates(directory="server/templates")
UPLOAD_DIR = "server/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ 추천 퀘스트
@router.post("/recommend", response_class=HTMLResponse)
async def recommend_routes(request: Request, categories: str = Form(...)):
    try:
        selected_categories = json.loads(categories)
    except json.JSONDecodeError:
        selected_categories = []
    
    recommended_routes = get_routes_by_categories(selected_categories)
    
    return templates.TemplateResponse("recommend.html", {
        "request": request,
        "routes": recommended_routes
    })

@router.post("/start-quest")
async def start_quest(request: Request):
    form_data = await request.form()
    quests_to_create = []
    
    # This logic rebuilds the list of quests from the submitted form data.
    # It groups data by index (0, 1, 2) from the form fields.
    i = 0
    while f"course_id_{i}" in form_data:
        # Only add the quest if a mission title was provided
        if form_data.get(f"mission_{i}"):
            quests_to_create.append({
                "course_id": form_data[f"course_id_{i}"],
                "mission": form_data[f"mission_{i}"],
                "place_name": form_data[f"place_name_{i}"],
                "description": form_data[f"description_{i}"],
                "address": form_data[f"address_{i}"],
                "lat": form_data[f"lat_{i}"],
                "lng": form_data[f"lng_{i}"],
            })
        i += 1
        
    if quests_to_create:
        create_quests(quests_to_create)
    
    return RedirectResponse(url="/api/quest", status_code=303)

# ✅ 퀘스트 목록 페이지
@router.get("/quest")
async def quest_course(request: Request):
    steps_data = get_all_quests()
    
    # Convert Decimal to float for JSON serialization in templates
    steps = []
    for step in steps_data:
        step_dict = dict(step)
        if 'lat' in step_dict and step_dict['lat'] is not None:
            step_dict['lat'] = float(step_dict['lat'])
        if 'lng' in step_dict and step_dict['lng'] is not None:
            step_dict['lng'] = float(step_dict['lng'])
        steps.append(step_dict)

    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": "기본",
        "steps": steps
    })

# ✅ 퀘스트 상세 페이지 - 개선된 버전
@router.get("/quest/{quest_id}")
async def quest_detail(request: Request, quest_id: int, result: str = "", theme: str = "기본"):
    # Get detailed quest information including photomission
    quest = get_quest_by_id(quest_id)
    
    # Create verification result based on the result parameter
    verification = None
    if result:
        if result == "success":
            verification = {
                "score": 85,
                "feedback": "축하합니다! 포토 미션을 성공적으로 완료했습니다. 훌륭한 사진이네요!",
                "mission_fulfilled": True
            }
        elif result == "fail":
            verification = {
                "score": 45,
                "feedback": "아쉽게도 포토 미션 요구사항을 충족하지 못했습니다. 미션 내용을 다시 확인하고 재도전해보세요!",
                "mission_fulfilled": False
            }
    
    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest,
        "result": result,
        "verification": verification,
        "theme": theme
    })

# ✅ 사용자 정의 퀘스트 입력 페이지
@router.get("/custom", response_class=HTMLResponse)
async def custom_input_page(request: Request, set_id: int = None):
    set_details = []
    if set_id:
        set_details = get_set_by_id(set_id)
    print(set_details)
    return templates.TemplateResponse("custom.html", {
        "request": request,
        "set_details": set_details
    })

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





