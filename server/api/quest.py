from fastapi import APIRouter
from pydantic import BaseModel
from server.services.quest_generate import create_main_graph

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