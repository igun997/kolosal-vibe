"""WebSocket handling for real-time streaming."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import traceback

from src.sessions.manager import get_session_manager

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


ws_manager = ConnectionManager()


@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming chat responses.

    Message format (client -> server):
    {
        "type": "chat",
        "prompt": "Create a todo app"
    }

    Message format (server -> client):
    {
        "type": "token" | "code" | "preview" | "error" | "complete",
        "content": "..."
    }
    """
    await ws_manager.connect(websocket, session_id)

    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session:
        await websocket.send_json({
            "type": "error",
            "content": "Session not found"
        })
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                prompt = data.get("prompt", "")

                try:
                    # Stream the response
                    for chunk in session.agent.stream_generate(prompt):
                        await websocket.send_json({
                            "type": chunk["type"],
                            "content": chunk["content"]
                        })

                    # After generation, deploy and get preview
                    preview = await session.deploy_and_preview()

                    if preview:
                        await websocket.send_json({
                            "type": "preview",
                            "content": {
                                "url": preview.url,
                                "token": preview.token
                            }
                        })

                    await websocket.send_json({
                        "type": "complete",
                        "content": {
                            "files": session.list_files()
                        }
                    })

                except Exception as e:
                    error_msg = f"{str(e)}\n{traceback.format_exc()}"
                    print(f"Chat error: {error_msg}")
                    await websocket.send_json({
                        "type": "error",
                        "content": str(e)
                    })

            elif data.get("type") == "update_code":
                # User manually edited code
                path = data.get("path")
                content = data.get("content")

                if path and content is not None:
                    session.update_file(path, content)

                    # Redeploy
                    preview = await session.deploy_and_preview()

                    if preview:
                        await websocket.send_json({
                            "type": "preview",
                            "content": {
                                "url": preview.url,
                                "token": preview.token
                            }
                        })

            elif data.get("type") == "set_model":
                # Change the AI model
                model = data.get("model")
                if model:
                    session.agent.set_model(model)
                    await websocket.send_json({
                        "type": "model_changed",
                        "content": {"model": model}
                    })

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
    except Exception as e:
        ws_manager.disconnect(session_id)
        print(f"WebSocket error: {e}")
