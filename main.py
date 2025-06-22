from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from server.api import recommend  # ✅ 올바른 경로로 import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="server/templates")
app.mount("/static", StaticFiles(directory="server/static"), name="static")

app.include_router(recommend.router, prefix="/api")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("category.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")

# ✅ 여기를 추가해야 python main.py 로 서버가 실행됩니다
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
