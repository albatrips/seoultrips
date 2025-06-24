from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from server.api.location import router as location_router
from server.api.quest import router as quest_router
from server.api.recommend import router as recommend_router

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
app.include_router(recommend_router, prefix="/app")

@app.get("/")
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

