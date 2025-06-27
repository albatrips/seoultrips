from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from server.api.location import router as location_router
from server.api.quest import router as quest_router
from server.api.recommend import router as recommend_router
from server.services.client import get_user, save_user
import pandas as pd

app = FastAPI()
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
async def show_categories(request: Request):
    return templates.TemplateResponse("category.html", {"request": request})

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
    
from fastapi import FastAPI, Request, UploadFile, File

import shutil
import os

UPLOAD_DIR = "server/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-photo")
async def upload_photo(request: Request, photo: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, photo.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": {
            "title": "업로드된 퀘스트 예시",
            "description": "사진이 업로드되었습니다!",
            "photo_url": f"/static/uploads/{photo.filename}"
        }
    })

# server/app.py 맨 아래에 잠깐 추가
if __name__ == "__main__":
    for r in app.routes:
        print(f"{r.path} -> {r.methods}")
