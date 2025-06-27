import json
from fastapi import APIRouter, Request, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi import HTTPException

from server.services.client import get_user
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
async def generate_quest(request: Request):
    body = await request.json()
    question = body.get("question")
    print("DEBUG question:", question)

    user = get_user()
    print("DEBUG user:", user)
    initial_state = QuestRequest(
        gender=user.get("gender"),
        age=user.get("age"),
        location=user.get("location"),
        travel_time=int(user.get("travel_time")),
        user_location=user.get("location"),
        question=question,
        category= "" if user.get("category") is None else user.get("category"),
    )

    graph = create_main_graph()
    final_state = await graph.ainvoke(initial_state)
    print("DEBUG final_state:", final_state.get("result"))

    # return {"result": final_state.get("result")}
    # return final_state.get("result")

    try:
        parsed = json.loads(final_state.get("result").replace("```", '').replace("json", ''))
        print(parsed)
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"LLM이 반환한 JSON 파싱 실패: {e}")
    return JSONResponse(content=parsed)