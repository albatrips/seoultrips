from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
#from api.recommend import router as recommend_router
from server.api.recommend import router as recommend_router
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 애플리케이션 생성
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Next.js 개발 서버
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")

# 라우터 등록
app.include_router(recommend_router, prefix="/api")

# 첫 화면: 테마 카테고리 선택
@app.get("/")
async def show_categories(request: Request):
    return templates.TemplateResponse("category.html", {"request": request})

# 퀘스트 페이지
@app.get("/quest")
async def quest_course(request: Request, theme: str = "추천 코스"):
    steps = [
        {"id": 1, "title": "A 명소 방문", "lat": 37.579617, "lng": 126.977041},
        {"id": 2, "title": "B 거리 걷기", "lat": 37.580146, "lng": 126.976892},
        {"id": 3, "title": "C 카페 인증", "lat": 37.580146, "lng": 126.976892}
    ]
    return templates.TemplateResponse("quest_course.html", {
        "request": request,
        "theme": theme,
        "steps": steps
    })
    


# ⬇️ 실행 진입점 추가
if __name__ == "__main__":
    import uvicorn
    # app 인스턴스를 직접 전달
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
    
