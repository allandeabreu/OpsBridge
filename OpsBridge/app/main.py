from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.system import router as system_router
from app.api.routes.tickets import router as tickets_router
from app.db.init_db import init_db

STATIC = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Create missing tables, preserve existing tickets.
    yield

app = FastAPI(
    title="OpsBridge",
    description="IT Support Ticket Management System",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(system_router)
app.include_router(tickets_router)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.get("/ui", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC / "index.html")
