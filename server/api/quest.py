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
    
    # 지역 정보 추출 - "지역명에서" 패턴 확인
    selected_region = None
    region_list = [
        "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
        "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
        "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구",
        "종로구", "중구", "중랑구"
    ]
    
    for region in region_list:
        if f"{region}에서" in question:
            selected_region = region
            break
    
    # user_location 결정 - 지역이 선택된 경우 해당 지역 사용, 아니면 기본 user location 사용
    user_location = selected_region if selected_region else user.get("location")
    
    print(f"DEBUG selected_region: {selected_region}")
    print(f"DEBUG user_location: {user_location}")
    
    initial_state = QuestRequest(
        gender=user.get("gender"),
        age=user.get("age"),
        location=user_location,  # 선택된 지역 또는 기본 위치
        travel_time=int(user.get("travel_time")),
        user_location=user_location,  # 선택된 지역 또는 기본 위치
        question=question,
        category= "" if user.get("category") is None else user.get("category"),
    )
    print("DEBUG initial_state:", initial_state)
    graph = create_main_graph()
    final_state = await graph.ainvoke(initial_state)
    print("DEBUG final_state:", final_state.get("result"))

    # return {"result": final_state.get("result")}
    # return final_state.get("result")

    try:
        parsed = json.loads(final_state.get("result").replace("```", '').replace("json", ''))
        print("DEBUG parsed quest data:", parsed)
        
        # 좌표 정보 확인
        if "quests" in parsed:
            for i, quest in enumerate(parsed["quests"]):
                lat = quest.get("lat")
                lng = quest.get("lng")
                location = quest.get("location", "Unknown")
                print(f"DEBUG Quest {i+1} - {location}: lat={lat}, lng={lng}")
                
        print(parsed)
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"LLM이 반환한 JSON 파싱 실패: {e}")
    return JSONResponse(content=parsed)