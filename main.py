from server.app import app
import uvicorn

# ✅ 여기를 추가해야 python main.py 로 서버가 실행됩니다
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
