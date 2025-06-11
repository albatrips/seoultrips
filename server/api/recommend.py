from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
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

    quest_steps = []
    for i, it in enumerate(items[:3]):
        quest_steps.append({
            "name": it.get("title"),
            "description": f"Visit {it.get('title')} and take a photo for your {theme} quest.",
            "id": i + 1
        })

    return templates.TemplateResponse("recommend.html", {
        "request": request,
        "theme": theme,
        "steps": quest_steps
    })
