from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests

router = APIRouter()
templates = Jinja2Templates(directory="server/templates")

@router.post("/recommend")
async def recommend(request: Request, theme: str = Form(...)):
    api_url = "https://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    params = {
        "serviceKey": "YOUR_SERVICE_KEY",
        "areaCode": 11,
        "numOfRows": 5,
        "pageNo": 1,
        "arrange": "O",
        "contentTypeId": 12,
        "MobileOS": "WEB",
        "MobileApp": "MicroQuestPassport",
        "_type": "json"
    }

    resp = requests.get(api_url, params=params)
    items = resp.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])

    steps = []
    for i, item in enumerate(items[:3]):
        steps.append({
            "id": i + 1,
            "title": item.get("title"),
            "lat": float(item.get("mapy", 37.57)),
            "lng": float(item.get("mapx", 126.98)),
            "description": f"{item.get('title')}에 방문하여 '{theme}' 퀘스트를 수행하세요."
        })

    request.app.state.current_quests = steps

    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": theme,
        "steps": steps
    })

@router.get("/quest/{quest_id}", response_class=HTMLResponse)
async def quest_detail(request: Request, quest_id: int):
    quests = getattr(request.app.state, "current_quests", [])

    if not quests or all(q["id"] != quest_id for q in quests):
        quest = {
            "id": quest_id,
            "title": "예시 퀘스트: 경복궁 방문",
            "lat": 37.579617,
            "lng": 126.977041,
            "description": "경복궁에 방문하여 인증샷을 찍어보세요!"
        }
    else:
        quest = next((q for q in quests if q["id"] == quest_id))

    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": quest
    })
