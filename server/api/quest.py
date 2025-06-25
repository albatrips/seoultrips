from fastapi import APIRouter
from pydantic import BaseModel
from server.services.quest_generate import create_main_graph
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form
router = APIRouter()

class QuestRequest(BaseModel):
    gender: str
    age: int
    location: str
    travel_time: int
    user_location: str
    question: str
    category: str

@router.post("/generate")
async def generate_quest(request: QuestRequest):
    graph = create_main_graph()
    initial_state = request.dict()
    final_state = await graph.ainvoke(initial_state)
    return final_state.get("result") 

templates = Jinja2Templates(directory="server/templates")
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