from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from server.api.recommend import router as recommend_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")

app.include_router(recommend_router, prefix="/api")

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
