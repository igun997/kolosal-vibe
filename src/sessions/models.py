"""Pydantic models for API requests/responses."""

from pydantic import BaseModel
from typing import Optional, List, Dict


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    model: Optional[str] = None  # AI model to use


class ModelInfo(BaseModel):
    """AI model information."""
    id: str
    name: str
    context_size: int = 0


class SessionResponse(BaseModel):
    """Response for session operations."""
    session_id: str
    status: str
    preview_url: Optional[str] = None
    files: Optional[List[str]] = None


class ChatRequest(BaseModel):
    """Request for chat/generate endpoint."""
    session_id: str
    prompt: str


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str
    code: Optional[str] = None
    files: List[str] = []
    preview_url: Optional[str] = None


class PreviewResponse(BaseModel):
    """Preview URL response."""
    url: Optional[str]
    token: Optional[str]


class FileInfo(BaseModel):
    """File information."""
    path: str
    name: str
    content: Optional[str] = None


class UpdateCodeRequest(BaseModel):
    """Request to update code file."""
    path: str
    content: str


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str  # chat, update_code
    prompt: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None


class StreamMessage(BaseModel):
    """Streaming response message."""
    type: str  # token, code, preview, complete, error
    content: Dict | str | None = None
