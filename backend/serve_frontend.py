from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from backend.main import app as api_app
except ModuleNotFoundError:
    from main import app as api_app

app = FastAPI(title="HAZM TUWAIQ Unified App")

# Expose existing API app under /api so frontend and backend share one origin.
app.mount("/api", api_app)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Serve all frontend assets/files.
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")


@app.get("/")
def home():
    index_file = FRONTEND_DIR / "login.html"
    if not index_file.exists():
        index_file = FRONTEND_DIR / "index.html"
    return FileResponse(str(index_file))
