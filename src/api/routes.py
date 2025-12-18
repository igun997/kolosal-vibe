"""REST API endpoints for the vibe coding app."""

from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.responses import HTMLResponse
from typing import List
import httpx
import os

from src.sessions.manager import SessionManager, get_session_manager
from src.sessions.models import (
    CreateSessionRequest,
    SessionResponse,
    ChatRequest,
    ChatResponse,
    PreviewResponse,
    FileInfo,
    ModelInfo,
)
from src.llm import KolosalClient

router = APIRouter()


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """Get available AI models from Kolosal."""
    api_key = os.getenv("KOLOSAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="KOLOSAL_API_KEY not configured")

    models = KolosalClient.list_models(api_key)
    return [
        ModelInfo(
            id=m.get("id", ""),
            name=m.get("name", m.get("id", "Unknown")),
            context_size=m.get("contextSize", 0),
        )
        for m in models
    ]


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest = None,
    manager: SessionManager = Depends(get_session_manager)
):
    """Create a new coding session with its own Daytona sandbox."""
    model = request.model if request else None
    session = await manager.create_session(model=model)
    return SessionResponse(
        session_id=session.id,
        status="active",
        preview_url=None
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Get session status and info."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.id,
        status=session.status,
        preview_url=session.preview_url,
        files=session.list_files()
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Destroy a session and its sandbox."""
    success = await manager.destroy_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "destroyed"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Non-streaming chat endpoint for code generation."""
    session = manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session.agent.generate_web_code(request.prompt)

    # Start preview server and get URL
    await session.deploy_and_preview()

    return ChatResponse(
        message=result.get("message", ""),
        code=result.get("code"),
        files=list(result.get("files", {}).keys()),
        preview_url=session.preview_url
    )


@router.get("/preview/{session_id}", response_model=PreviewResponse)
async def get_preview(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Get the preview URL for a session's sandbox."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    preview = await session.get_preview_url()
    return PreviewResponse(
        url=preview.url if preview else None,
        token=preview.token if preview else None
    )


@router.get("/files/{session_id}", response_model=List[FileInfo])
async def list_files(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """List files in the session's workspace."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    files = session.list_files()
    return [
        FileInfo(path=f, name=f)
        for f in files
    ]


@router.get("/files/{session_id}/{path:path}")
async def get_file(
    session_id: str,
    path: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Get contents of a specific file."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    content = session.get_file(path)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {"path": path, "content": content}


@router.put("/files/{session_id}/{path:path}")
async def update_file(
    session_id: str,
    path: str,
    content: dict,
    manager: SessionManager = Depends(get_session_manager)
):
    """Update a file in the session's workspace."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.update_file(path, content.get("content", ""))

    # Refresh preview
    await session.deploy_and_preview()

    return {"status": "updated", "path": path}


@router.get("/proxy/{session_id}/{path:path}")
async def proxy_preview(
    request: Request,
    session_id: str,
    path: str = "",
    manager: SessionManager = Depends(get_session_manager)
):
    """Proxy preview requests with proper Daytona authentication."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get preview URL and token
    if not session.preview_url or not session.preview_token:
        preview = await session.get_preview_url()
        if not preview:
            raise HTTPException(status_code=404, detail="Preview not available")

    # Construct target URL with path
    target_url = session.preview_url
    if path:
        target_url = f"{session.preview_url.rstrip('/')}/{path}"

    # Add query parameters (except cache-busting 'v')
    query_params = dict(request.query_params)
    query_params.pop('v', None)  # Remove cache-buster
    if query_params:
        query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
        target_url = f"{target_url}?{query_string}"

    # Fetch with auth header
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(
                target_url,
                headers={
                    "x-daytona-preview-token": session.preview_token or ""
                }
            )

            # Return response with appropriate content type
            content_type = response.headers.get("content-type", "text/html")

            return Response(
                content=response.content,
                media_type=content_type,
                status_code=response.status_code
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")
