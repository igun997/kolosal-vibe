"""Daytona Sandbox Manager - Creates and manages sandboxes for code execution."""

from daytona_sdk import Daytona, DaytonaConfig
from typing import Optional


class SandboxManager:
    """Manages Daytona sandboxes for safe code execution."""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        config = DaytonaConfig(api_key=api_key, api_url=api_url)
        self.daytona = Daytona(config)
        self.sandbox = None
        self.sandbox_id = None

    def create_sandbox(self) -> str:
        """Create a new sandbox and return its ID."""
        self.sandbox = self.daytona.create()
        self.sandbox_id = self.sandbox.id
        return self.sandbox_id

    def execute_code(self, code: str, language: str = "python") -> dict:
        """Execute code in the sandbox and return the result."""
        if not self.sandbox:
            self.create_sandbox()

        if language == "python":
            file_path = "/tmp/script.py"
            self.sandbox.fs.upload_file(code.encode(), file_path)  # (src_content, dst_path)
            result = self.sandbox.process.exec(f"python3 {file_path}")
        elif language == "javascript":
            file_path = "/tmp/script.js"
            self.sandbox.fs.upload_file(code.encode(), file_path)  # (src_content, dst_path)
            result = self.sandbox.process.exec(f"node {file_path}")
        elif language == "bash":
            result = self.sandbox.process.exec(code)
        else:
            return {"error": f"Unsupported language: {language}", "stdout": "", "stderr": "", "exit_code": 1}

        # Parse the result - Daytona SDK uses 'result' not 'stdout'
        stdout = result.result if hasattr(result, 'result') else ""
        stderr = ""

        # Check artifacts for stderr if available
        if hasattr(result, 'artifacts') and result.artifacts:
            if hasattr(result.artifacts, 'stderr'):
                stderr = result.artifacts.stderr or ""

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": result.exit_code if hasattr(result, 'exit_code') else 0
        }

    def execute_command(self, command: str) -> dict:
        """Execute a shell command in the sandbox."""
        if not self.sandbox:
            self.create_sandbox()

        result = self.sandbox.process.exec(command)
        return {
            "stdout": result.result if hasattr(result, 'result') else "",
            "stderr": "",
            "exit_code": result.exit_code if hasattr(result, 'exit_code') else 0
        }

    def upload_file(self, path: str, content: str) -> bool:
        """Upload a file to the sandbox."""
        if not self.sandbox:
            self.create_sandbox()

        try:
            # Try SDK method first
            self.sandbox.fs.upload_file(content.encode(), path)
        except Exception as e:
            print(f"[Sandbox] SDK upload failed, using fallback: {e}")
            # Fallback: use base64 encoding and shell command
            import base64
            encoded = base64.b64encode(content.encode()).decode()
            # Create directory if needed
            dir_path = "/".join(path.split("/")[:-1])
            if dir_path:
                self.sandbox.process.exec(f"mkdir -p {dir_path}")
            # Write file using base64 decode
            self.sandbox.process.exec(f"echo '{encoded}' | base64 -d > {path}")
        return True

    def download_file(self, path: str) -> str:
        """Download a file from the sandbox."""
        if not self.sandbox:
            raise RuntimeError("No sandbox created")

        content = self.sandbox.fs.download_file(path)
        return content.decode() if isinstance(content, bytes) else content

    def get_preview_url(self, port: int = 8000):
        """Get preview URL for a running server in the sandbox.

        Returns a PortPreviewUrl object with .url and .token attributes.
        """
        if not self.sandbox:
            raise RuntimeError("No sandbox created")

        return self.sandbox.get_preview_link(port)

    def destroy(self):
        """Destroy the current sandbox."""
        if self.sandbox:
            try:
                self.daytona.delete(self.sandbox)
            except Exception:
                pass  # Ignore errors during cleanup
            self.sandbox = None
            self.sandbox_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()
