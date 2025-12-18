#!/usr/bin/env python3
"""
Vibe Coding App - Web-based AI Code Generator with Live Preview

Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8080
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

from src.api.routes import router as api_router
from src.api.websocket import router as ws_router
from src.sessions.manager import get_session_manager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("Starting Vibe Coding App...")
    yield
    # Shutdown
    print("Shutting down...")
    manager = get_session_manager()
    await manager.cleanup_all()
    print("All sessions cleaned up.")


app = FastAPI(
    title="Vibe Coding App",
    description="AI-powered code generator with live preview",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        # Serve index.html for all non-API routes (SPA routing)
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "Vibe Coding API",
            "docs": "/docs",
            "frontend": "Run 'npm run dev' in frontend/ directory"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
