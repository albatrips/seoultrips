from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from server.api import recommend  # ✅ 올바른 경로로 수정
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")

app.include_router(recommend.router)  # prefix 제거


@app.get("/")
async def root():
    return {
        "message": "서버 실행 중입니다. → /quest 또는 /api/recommend 확인하세요."
    }

@app.on_event("startup")
async def startup_event():
    app.state.current_quests = [
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
