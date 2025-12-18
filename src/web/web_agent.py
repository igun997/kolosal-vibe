"""Web-focused code agent that generates HTML/CSS/JS."""

from typing import Optional, Generator, List, Dict
import asyncio
import re

from src.agent import CodeAgent
from src.sandbox import SandboxManager


class WebCodeAgent(CodeAgent):
    """Extended agent for web development with preview support."""

    WORKSPACE_DIR = "/home/daytona/project"

    WEB_SYSTEM_PROMPT = """You are an expert web developer building apps for users. You create complete, working web applications.

HOW TO RESPOND:
1. First, briefly explain what you're going to build (1-2 sentences)
2. Then output the code files (these will be deployed automatically)
3. Finally, describe what was created and how to use it

CODING RULES:
- Generate complete HTML, CSS, and JavaScript files
- Use modern, responsive CSS (flexbox, grid)
- Use Tailwind CSS via CDN for quick styling
- Make designs visually appealing with good colors and spacing
- Ensure the app is fully functional

FILE OUTPUT FORMAT (required for deployment):
```index.html
<!DOCTYPE html>
<html>...</html>
```

```styles.css
/* styles */
```

```script.js
// code
```

RESPONSE STYLE:
- Keep explanations brief and friendly
- Don't explain the code in detail - users will see the live preview
- Focus on what the app does, not how it's coded
- Use bullet points for features"""

    def __init__(
        self,
        kolosal_api_key: str,
        daytona_api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(kolosal_api_key, daytona_api_key, model)
        self.project_files: Dict[str, str] = {}
        self.server_running = False

    def _ensure_sandbox(self):
        """Ensure sandbox is created and workspace exists."""
        super()._ensure_sandbox()
        self._setup_workspace()

    def _setup_workspace(self):
        """Setup workspace directory in sandbox."""
        if self.sandbox:
            result = self.sandbox.execute_command(f"mkdir -p {self.WORKSPACE_DIR}")
            print(f"[WebCodeAgent] Created workspace: {self.WORKSPACE_DIR} (exit: {result.get('exit_code', 'unknown')})")

    def generate_web_code(self, prompt: str) -> dict:
        """Generate web code from prompt."""
        messages = [
            {"role": "system", "content": self.WEB_SYSTEM_PROMPT},
        ]

        # Add history context (last 3 exchanges)
        for item in self.history[-3:]:
            if item.get("action") == "generate_web":
                messages.append({
                    "role": "user",
                    "content": item.get("prompt", "")
                })
                # Add file list as context
                files_summary = ", ".join(item.get("files", []))
                messages.append({
                    "role": "assistant",
                    "content": f"I created the following files: {files_summary}"
                })

        messages.append({"role": "user", "content": prompt})

        response = self.llm.chat(messages, temperature=0.5, max_tokens=8192)

        # Parse multi-file response
        files = self._parse_web_files(response)

        # Upload files to sandbox
        self._ensure_sandbox()

        for filename, content in files.items():
            path = f"{self.WORKSPACE_DIR}/{filename}"
            self.sandbox.upload_file(path, content)
            self.project_files[filename] = content

        self.history.append({
            "action": "generate_web",
            "prompt": prompt,
            "files": list(files.keys()),
            "raw_response": response
        })

        return {
            "message": "Code generated successfully",
            "files": files,
            "code": files.get("index.html", "")
        }

    def stream_generate(self, prompt: str) -> Generator[dict, None, None]:
        """Stream generate web code with real-time updates."""
        messages = [
            {"role": "system", "content": self.WEB_SYSTEM_PROMPT},
        ]

        # Add history context
        for item in self.history[-3:]:
            if item.get("action") == "generate_web":
                messages.append({
                    "role": "user",
                    "content": item.get("prompt", "")
                })
                files_summary = ", ".join(item.get("files", []))
                messages.append({
                    "role": "assistant",
                    "content": f"I created these files: {files_summary}"
                })

        messages.append({"role": "user", "content": prompt})

        full_response = ""

        # Use streaming from LLM
        for chunk in self.llm.chat(messages, stream=True, max_tokens=8192, temperature=0.5):
            full_response += chunk
            yield {"type": "token", "content": chunk}

        # Parse and upload files
        print(f"[WebCodeAgent] Parsing files from response ({len(full_response)} chars)")
        files = self._parse_web_files(full_response)
        print(f"[WebCodeAgent] Parsed {len(files)} files: {list(files.keys())}")

        self._ensure_sandbox()

        for filename, content in files.items():
            path = f"{self.WORKSPACE_DIR}/{filename}"
            print(f"[WebCodeAgent] Uploading {filename} ({len(content)} chars)")
            self.sandbox.upload_file(path, content)
            self.project_files[filename] = content
            yield {
                "type": "code",
                "content": {"filename": filename, "code": content}
            }

        self.history.append({
            "action": "generate_web",
            "prompt": prompt,
            "files": list(files.keys())
        })

    def _parse_web_files(self, response: str) -> Dict[str, str]:
        """Parse multiple files from LLM response."""
        files = {}

        # Pattern 1: ```filename.ext format (filename on same line as backticks)
        pattern1 = r"```(\S+\.(?:html|css|js|json))\s*\n(.*?)```"
        matches = re.findall(pattern1, response, re.DOTALL | re.IGNORECASE)
        for filename, content in matches:
            filename = filename.strip()
            files[filename] = content.strip()

        # Pattern 2: ```language format with common language identifiers
        if "index.html" not in files:
            # Try various HTML patterns
            html_patterns = [
                r"```html\s*\n(.*?)```",
                r"```HTML\s*\n(.*?)```",
                r"```htm\s*\n(.*?)```",
            ]
            for pattern in html_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    files["index.html"] = match.group(1).strip()
                    break

        if "styles.css" not in files and "style.css" not in files:
            css_patterns = [
                r"```css\s*\n(.*?)```",
                r"```CSS\s*\n(.*?)```",
            ]
            for pattern in css_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    files["styles.css"] = match.group(1).strip()
                    break

        if "script.js" not in files and "app.js" not in files:
            js_patterns = [
                r"```javascript\s*\n(.*?)```",
                r"```js\s*\n(.*?)```",
                r"```JavaScript\s*\n(.*?)```",
                r"```JS\s*\n(.*?)```",
            ]
            for pattern in js_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    files["script.js"] = match.group(1).strip()
                    break

        # Fallback: if no files found, try to extract any code block
        if not files:
            # Try generic code block
            generic_pattern = r"```(?:\w*)\s*\n(.*?)```"
            matches = re.findall(generic_pattern, response, re.DOTALL)
            if matches:
                # Use the first code block as index.html
                content = matches[0].strip()
                # Check if it looks like HTML
                if content.startswith("<!DOCTYPE") or content.startswith("<html") or "<" in content:
                    files["index.html"] = content
                else:
                    # Wrap in HTML
                    files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div id="app" class="container mx-auto p-4">
        <script>{content}</script>
    </div>
</body>
</html>"""

        # Ultimate fallback: create a basic HTML file
        if not files:
            # Check if response contains HTML-like content
            if "<!DOCTYPE" in response or "<html" in response:
                # Extract HTML from response
                html_start = response.find("<!DOCTYPE")
                if html_start == -1:
                    html_start = response.find("<html")
                if html_start != -1:
                    files["index.html"] = response[html_start:].strip()
            else:
                # Create a placeholder with instructions
                files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-2xl">
        <h1 class="text-2xl font-bold mb-4">Generated Content</h1>
        <pre class="bg-gray-100 p-4 rounded overflow-auto text-sm">{response[:2000]}</pre>
    </div>
</body>
</html>"""

        return files

    async def start_preview_server(self):
        """Start HTTP server in sandbox for preview."""
        if self.server_running:
            return

        if not self.sandbox:
            return

        # Kill any existing server
        self.sandbox.execute_command("pkill -f 'python3 -m http.server' 2>/dev/null || true")

        # Start server in background
        cmd = f"cd {self.WORKSPACE_DIR} && nohup python3 -m http.server 8000 > /dev/null 2>&1 &"
        self.sandbox.execute_command(cmd)

        # Wait for server to start
        await asyncio.sleep(1)
        self.server_running = True

    def get_project_files(self) -> List[str]:
        """Get list of project files."""
        return list(self.project_files.keys())

    def get_file_content(self, filename: str) -> Optional[str]:
        """Get content of a specific file."""
        return self.project_files.get(filename)

    def update_file(self, filename: str, content: str):
        """Update a file in the sandbox."""
        if not self.sandbox:
            return

        path = f"{self.WORKSPACE_DIR}/{filename}"
        self.sandbox.upload_file(path, content)
        self.project_files[filename] = content
