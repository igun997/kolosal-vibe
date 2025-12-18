# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kolosal Vibes is an AI-powered vibe coding platform that uses Kolosal AI for LLM capabilities and Daytona sandboxes for safe code execution. It has two interfaces:

1. **CLI Mode**: Terminal-based interface for generating and executing Python/JavaScript/Bash code
2. **Web Mode**: Browser-based "vibe coding" interface (like Bolt.new/v0.dev) for building web apps with live preview

## Commands

```bash
# CLI Mode
python main.py

# Web Mode (run both in separate terminals)
uvicorn app:app --reload --host 0.0.0.0 --port 8080
cd frontend && npm run dev  # runs on http://localhost:5173

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# Build frontend for production
cd frontend && npm run build
```

## Architecture

### CLI Mode
```
main.py          → CLI entry point, Rich console
src/agent.py     → CodeAgent: LLM generation + sandbox execution + auto-fix
src/llm.py       → KolosalClient: OpenAI-compatible API wrapper
src/sandbox.py   → SandboxManager: Daytona SDK wrapper
```

### Web Mode
```
app.py                    → FastAPI entry point
src/api/routes.py         → REST endpoints (sessions, chat, preview, files, models)
src/api/websocket.py      → WebSocket for streaming LLM responses
src/sessions/manager.py   → Session lifecycle, sandbox per session
src/sessions/models.py    → Pydantic request/response models
src/web/web_agent.py      → WebCodeAgent: generates HTML/CSS/JS, serves preview

frontend/                 → React + Vite + Tailwind PWA
  src/stores/store.ts     → Zustand state management
  src/components/         → ChatPanel, ChatMessage, PreviewPanel, Toolbar, Layout
  vite.config.ts          → PWA configuration with vite-plugin-pwa
  tailwind.config.js      → Kolosal brand colors (kolosal, accent)
```

**Web Flow:**
1. User creates session → Daytona sandbox spins up
2. User describes app in chat → WebSocket streams LLM response
3. WebCodeAgent parses files from ` ```filename.html ` blocks
4. Files uploaded to sandbox `/workspace/project/`
5. HTTP server starts → `sandbox.get_preview_link(8000)` returns preview URL
6. Preview displayed in iframe with live updates

## Key Implementation Details

- **LLM Client**: OpenAI SDK at `https://api.kolosal.ai/v1`, default model `meta-llama/llama-4-maverick-17b-128e-instruct`
- **Model Switching**: `/api/models` endpoint fetches available models, frontend allows switching via dropdown
- **Code Extraction**: Regex parses ` ```filename.ext ` blocks in `WebCodeAgent._parse_web_files()`
- **Preview Server**: Python's `http.server` on port 8000 in sandbox
- **Session Management**: One sandbox per session, 30-min inactivity timeout
- **WebSocket Protocol**: `{type: "chat", prompt}` → streams `{type: "token|code|preview|complete"}`
- **PWA**: Service worker with offline caching, installable on desktop/mobile

## Environment Variables

Required in `.env`:
- `KOLOSAL_API_KEY` - Kolosal AI API key
- `DAYTONA_API_KEY` - Daytona sandbox API key
- `DAYTONA_API_URL` (optional) - defaults to `https://app.daytona.io/api`

## Supported Languages

- **CLI Mode**: Python, JavaScript, Bash
- **Web Mode**: HTML, CSS, JavaScript (generates web apps)

## Brand Colors

Defined in `frontend/tailwind.config.js`:
- `kolosal` - Dark theme colors based on `#0D0E0F`
- `accent` - Indigo accent colors based on `#6366F1`
