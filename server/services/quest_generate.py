from pathlib import Path

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import HTTPException
from server.services.korea_tour_api import get_location_based_list
from server.api.location import get_sigungu_code
from langchain_core.messages import SystemMessage, HumanMessage
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class QuestState(TypedDict):
    # 가장 처음에 입력 받을 항목
    gender: str
    age: int
    location: str
    travel_time: int
    user_location: str
    question: str

    # 유저의 첫번째 선택 항목
    category: str

    # 엑셀 데이터
    excel_data: Dict[str, Any]
    # 관광_국문.API 데이터
    api_data: object
    # 퀘스트 생성 결과
    result: object

def init_state(state):
    """
    특정 지역구의 관광지 정보를 조회합니다.
    """
    district_name = state['location']
    sigungu_code = get_sigungu_code(district_name)
    if sigungu_code is None:
        raise HTTPException(status_code=404, detail=f"District '{district_name}' not found.")

    try:
        data = get_location_based_list(area_code=1, sigungu_code=sigungu_code)
        # print('\n\n\n\ndata', data, '\n\n\n\n')
        BASE = Path(__file__).resolve().parents[2]
        csv_path = BASE / 'place_name.csv'
        # print('\n\n\n\ncsv_path', csv_path, '\n\n\n\n')
        excel_data = pd.read_csv(csv_path, encoding='utf-8')

        return {"api_data": data, "excel_data": excel_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

def create_main_graph():
    graph = StateGraph(QuestState)
    graph.add_node("init_state", init_state)
    graph.add_node("quest_generate", quest_generate)
    graph.set_entry_point("init_state")
    graph.add_edge("init_state", "quest_generate")
    graph.add_edge("quest_generate", END)
    return graph.compile()


class QuestGeneratorPrompt:
    system="""
        너는 여행지의 놀거리 및 여행 콘텐츠를 큐레이션하는 여행 플래너 봇이다.
        사용자의 맞춤형 여행 플랜을 제안해야한다.
        사용자는 재미를 느끼며 여행하는 자들이기 때문에, 퀘스트 기반 여행 일정을 설계해야한다.

        [사용자 정보]
        - 성별
        - 연령 
        - 여행 테마
        - 출발 위치
        - 여행 시간
        - 질문 
        - 장소 

        [요청사항]
        - 위 사용자 정보와 질문을 토대로 퀘스트를 설계
        - 퀘스트는 관광_국문.API에서 데이터를 가져와 
        - 설계한 퀘스트 Output은 json으로 반환
        - 장소는 대한민국 서울 고정
        - 퀘스트는 3개 제안
        - 첫번째 퀘스트는 무조건 관광지 및 구경할 수 있는 곳으로 
        - 퀘스트 장소 가져오는 조건은 사용자 출발 위치와 가까운곳으로 우선 지정
        - 각 퀘스트는 `mission_name + location + description + expected_time` 구조
        - 각 퀘스트끼리 하나의 루트처럼 자연스럽게 이어지도록 구성
        - 장소 간 이동 시간과 운영시간 고려하여 추천
        - 실제 운영하는 /존재하는 장소로 추천
        - 전시/카페 등 운영시간이 있는 경우 명시
        - 여행 시간 내 수행 가능하도록 설계
        - 여행 시간이 지정되지 않았을때 전체 퀘스트는 1시간 반 내로 진행할 수 있도록 구성
        - 퀘스트는 장소가서 사진찍기, 카페가서 시간보내기, 산(공원) 걷기, 식당가서 00 먹기 등 다양한 엑티비티로 구성
        """
    human="""
        [사용자 정보]
        - 성별 : {gender} 성별
        - 연령 : {age} 나이
        - 여행 테마: {category} 카테고리
        - 출발 위치: {user_location} 출발 위치
        - 여행 시간: {travel_time} 여행 시간
        - 질문 : {question} 질문
        - 퀘스트 장소 : 
            {excel_data}
            {api_data}

        OUTPUT:
        """

async def quest_generate(state: QuestState):
    gender=state['gender']
    age=state['age']
    category=state['category']
    user_location=state['user_location']
    travel_time=state['travel_time']
    question=state['question']
    excel_data=state['excel_data']
    api_data=state['api_data']
    
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash",
    # )
    llm = ChatOpenAI(
        model="gpt-4o-mini"
    )

    messages = [
    SystemMessage(
        content=QuestGeneratorPrompt.system
    ),
    HumanMessage(
        content=QuestGeneratorPrompt.human.format(
            gender=gender,
            age=age,
            category=category,
            user_location=user_location,
            travel_time=travel_time,
            question=question,
            excel_data=excel_data,
            api_data=api_data,
        )
    ),
]

    response = await llm.ainvoke(messages)
    # print(response)
    # print(response.content)
    return {"result": response.content}

