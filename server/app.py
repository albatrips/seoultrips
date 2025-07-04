from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from server.api.location import router as location_router
from server.api.quest import router as quest_router
from server.api.recommend import router as recommend_router
from server.api.image_upload import router as image_upload_router
from server.services.client import get_user, save_user, get_all_categories, get_all_quests
from server.utils import CustomJSONEncoder
import pandas as pd

app = FastAPI()

jsonable_encoder.default = CustomJSONEncoder().default

app.include_router(recommend_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")

app.include_router(location_router, prefix="/api")
app.include_router(quest_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(image_upload_router, prefix="/api")

@app.get("/")
async def read_root(request: Request):
    user_data = get_user()
    try:
        df = pd.read_csv('seoul_sigungu_codes.csv')
        print('df', df)
        sigungu_list = df['name'].tolist()
    except FileNotFoundError:
        sigungu_list = []
    return templates.TemplateResponse("initial.html", {"request": request, "user": user_data, "sigungu_list": sigungu_list})

@app.post("/create-user")
async def handle_create_user(
    age: int = Form(...),
    gender: str = Form(...),
    location: str = Form(...),
    travel_time: int = Form(...)
):
    save_user(age, gender, location, travel_time)
    return RedirectResponse(url="/category", status_code=303)

@app.get("/category")
async def category_page(request: Request):
    categories = get_all_categories()
    return templates.TemplateResponse("category.html", {"request": request, "categories": categories})

@app.get("/api/check-quests")
async def check_quests():
    """퀘스트 존재 여부를 확인하는 API"""
    try:
        quests = get_all_quests()
        has_quests = len(quests) > 0
        return JSONResponse(content={"hasQuests": has_quests, "questCount": len(quests)})
    except Exception as e:
        print(f"퀘스트 확인 중 오류: {e}")
        return JSONResponse(content={"hasQuests": False, "questCount": 0})

@app.get("/quest")
async def quest_course(request: Request, theme: str = "추천 코스"):
    steps = [
        {"id": 1, "title": "A 명소 방문", "lat": 37.579617, "lng": 126.977041},
        {"id": 2, "title": "B 거리 걷기", "lat": 37.580146, "lng": 126.976892},
        {"id": 3, "title": "C 카페 인증", "lat": 37.579617, "lng": 126.977041}
    ]
    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": theme,
        "steps": steps
    })

# server/app.py 맨 아래에 잠깐 추가
if __name__ == "__main__":
    for r in app.routes:
        print(f"{r.path} -> {r.methods}")
