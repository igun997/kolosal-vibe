"""Session management for sandbox lifecycle."""

from typing import Dict, Optional
import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os

from src.web.web_agent import WebCodeAgent


@dataclass
class Session:
    """Represents a coding session with its own sandbox."""

    id: str
    agent: WebCodeAgent
    status: str = "active"
    preview_url: Optional[str] = None
    preview_token: Optional[str] = None
    files: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    async def get_preview_url(self):
        """Get preview URL from sandbox."""
        if self.agent.sandbox and self.agent.sandbox.sandbox:
            preview = self.agent.sandbox.get_preview_url(8000)
            self.preview_url = preview.url
            self.preview_token = preview.token
            return preview
        return None

    async def deploy_and_preview(self):
        """Deploy current code and return preview URL."""
        await self.agent.start_preview_server()
        return await self.get_preview_url()

    def list_files(self) -> list:
        """List files in workspace."""
        return self.agent.get_project_files()

    def get_file(self, path: str) -> Optional[str]:
        """Get file content."""
        return self.agent.get_file_content(path)

    def update_file(self, path: str, content: str):
        """Update file in sandbox."""
        self.agent.update_file(path, content)


class SessionManager:
    """Manages multiple coding sessions."""

    _instance: Optional["SessionManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.sessions: Dict[str, Session] = {}
        self.kolosal_api_key = os.getenv("KOLOSAL_API_KEY")
        self.daytona_api_key = os.getenv("DAYTONA_API_KEY")
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = True

    async def create_session(self, model: Optional[str] = None) -> Session:
        """Create a new session with its own sandbox."""
        session_id = str(uuid.uuid4())[:8]

        agent = WebCodeAgent(
            kolosal_api_key=self.kolosal_api_key,
            daytona_api_key=self.daytona_api_key,
            model=model
        )

        # Initialize sandbox in background
        await asyncio.to_thread(agent._ensure_sandbox)

        session = Session(
            id=session_id,
            agent=agent
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
        return session

    async def destroy_session(self, session_id: str) -> bool:
        """Destroy a session and cleanup its sandbox."""
        session = self.sessions.pop(session_id, None)
        if session:
            await asyncio.to_thread(session.agent.cleanup)
            return True
        return False

    async def cleanup_inactive(self, max_age_minutes: int = 30):
        """Cleanup sessions inactive for too long."""
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)

        to_remove = [
            sid for sid, session in self.sessions.items()
            if session.last_activity < cutoff
        ]

        for sid in to_remove:
            await self.destroy_session(sid)

    async def cleanup_all(self):
        """Cleanup all sessions."""
        for session_id in list(self.sessions.keys()):
            await self.destroy_session(session_id)


# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """FastAPI dependency to get session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
