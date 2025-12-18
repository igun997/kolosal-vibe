"""Code Agent - Generates and executes code using LLM + Daytona sandbox."""

from .llm import KolosalClient
from .sandbox import SandboxManager
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()


class CodeAgent:
    """Agent that generates code with LLM and executes it in Daytona sandbox."""

    MAX_RETRIES = 3

    def __init__(
        self,
        kolosal_api_key: str,
        daytona_api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.llm = KolosalClient(api_key=kolosal_api_key, model=model)
        self.daytona_api_key = daytona_api_key
        self.sandbox: Optional[SandboxManager] = None
        self.history: list[dict] = []

    def set_model(self, model: str):
        """Change the active AI model."""
        self.llm.set_model(model)

    def _ensure_sandbox(self):
        """Ensure sandbox is created."""
        if self.sandbox is None:
            console.print("[yellow]Creating Daytona sandbox...[/yellow]")
            self.sandbox = SandboxManager(api_key=self.daytona_api_key)
            self.sandbox.create_sandbox()
            console.print(f"[green]Sandbox created: {self.sandbox.sandbox_id}[/green]")

    def generate(self, prompt: str, language: str = "python") -> dict:
        """Generate code from a prompt."""
        console.print(Panel(f"[bold]Generating {language} code...[/bold]"))

        result = self.llm.generate_code(prompt, language)

        # Display generated code
        syntax = Syntax(result["code"], language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"Generated {language.upper()} Code"))

        self.history.append({
            "action": "generate",
            "prompt": prompt,
            "code": result["code"],
            "language": language
        })

        return result

    def execute(self, code: str, language: str = "python") -> dict:
        """Execute code in the sandbox."""
        self._ensure_sandbox()

        console.print(Panel(f"[bold]Executing {language} code...[/bold]"))

        result = self.sandbox.execute_code(code, language)

        # Display result
        if result.get("stdout"):
            console.print(Panel(result["stdout"], title="Output", border_style="green"))
        if result.get("stderr"):
            console.print(Panel(result["stderr"], title="Errors", border_style="red"))

        self.history.append({
            "action": "execute",
            "code": code,
            "language": language,
            "result": result
        })

        return result

    def run(self, prompt: str, language: str = "python", auto_fix: bool = True) -> dict:
        """Generate and execute code, with optional auto-fix on errors."""
        # Generate code
        gen_result = self.generate(prompt, language)
        code = gen_result["code"]

        # Execute code
        exec_result = self.execute(code, language)

        # Auto-fix on error
        retries = 0
        while auto_fix and exec_result.get("stderr") and retries < self.MAX_RETRIES:
            retries += 1
            console.print(f"[yellow]Error detected. Attempting fix ({retries}/{self.MAX_RETRIES})...[/yellow]")

            # Get fixed code from LLM
            fix_result = self.llm.analyze_error(code, exec_result["stderr"], language)
            code = fix_result["code"]

            # Display fixed code
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Fixed Code (Attempt {retries})"))

            # Re-execute
            exec_result = self.execute(code, language)

            if not exec_result.get("stderr"):
                console.print("[green]Code fixed successfully![/green]")
                break

        return {
            "prompt": prompt,
            "code": code,
            "language": language,
            "output": exec_result.get("stdout", ""),
            "errors": exec_result.get("stderr", ""),
            "exit_code": exec_result.get("exit_code", 0),
            "retries": retries
        }

    def chat(self, message: str) -> str:
        """Have a conversation with the agent."""
        # Build conversation history
        messages = [
            {
                "role": "system",
                "content": """You are a helpful coding assistant. You can:
1. Generate code when asked
2. Explain code concepts
3. Help debug issues
4. Answer programming questions

When generating code, wrap it in triple backticks with the language identifier.
Be concise and helpful."""
            }
        ]

        # Add history context
        for item in self.history[-5:]:  # Last 5 items
            if item["action"] == "generate":
                messages.append({
                    "role": "user",
                    "content": f"Generate code: {item['prompt']}"
                })
                messages.append({
                    "role": "assistant",
                    "content": f"```{item['language']}\n{item['code']}\n```"
                })

        messages.append({"role": "user", "content": message})

        response = self.llm.chat(messages)
        console.print(Markdown(response))

        return response

    def cleanup(self):
        """Clean up resources."""
        if self.sandbox:
            console.print("[yellow]Destroying sandbox...[/yellow]")
            self.sandbox.destroy()
            self.sandbox = None
            console.print("[green]Sandbox destroyed.[/green]")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
