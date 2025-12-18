#!/usr/bin/env python3
"""Mini Bolt - AI Code Generator & Executor using Kolosal AI + Daytona Sandbox."""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import CodeAgent

console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                     🚀 MINI BOLT                             ║
║           AI Code Generator & Executor                       ║
║         Powered by Kolosal AI + Daytona Sandbox              ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
**Commands:**
- `/run <prompt>` - Generate and execute code
- `/gen <prompt>` - Generate code only (no execution)
- `/exec` - Execute the last generated code
- `/lang <python|javascript|bash>` - Change language
- `/clear` - Clear conversation history
- `/help` - Show this help
- `/quit` or `/exit` - Exit the program

**Examples:**
- `/run create a function that calculates fibonacci numbers and test it with n=10`
- `/gen write a web scraper for a simple website`
- `/lang javascript`
- Just type normally to chat with the AI
"""


def main():
    load_dotenv()

    # Get API key from environment or use the provided one
    api_key = os.getenv("KOLOSAL_API_KEY")
    daytona_key = os.getenv("DAYTONA_API_KEY")

    if not api_key:
        console.print("[red]Error: KOLOSAL_API_KEY not set in environment[/red]")
        console.print("Set it in .env file or export KOLOSAL_API_KEY=your_key")
        sys.exit(1)

    console.print(BANNER, style="bold cyan")
    console.print(Markdown(HELP_TEXT))

    current_language = "python"
    last_code = None

    with CodeAgent(kolosal_api_key=api_key, daytona_api_key=daytona_key) as agent:
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    parts = user_input.split(" ", 1)
                    cmd = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""

                    if cmd in ["/quit", "/exit", "/q"]:
                        console.print("[yellow]Goodbye![/yellow]")
                        break

                    elif cmd == "/help":
                        console.print(Markdown(HELP_TEXT))

                    elif cmd == "/run":
                        if not args:
                            console.print("[red]Usage: /run <prompt>[/red]")
                            continue
                        result = agent.run(args, language=current_language)
                        last_code = result["code"]

                    elif cmd == "/gen":
                        if not args:
                            console.print("[red]Usage: /gen <prompt>[/red]")
                            continue
                        result = agent.generate(args, language=current_language)
                        last_code = result["code"]

                    elif cmd == "/exec":
                        if not last_code:
                            console.print("[red]No code to execute. Use /gen first.[/red]")
                            continue
                        agent.execute(last_code, language=current_language)

                    elif cmd == "/lang":
                        if args.lower() in ["python", "javascript", "bash"]:
                            current_language = args.lower()
                            console.print(f"[green]Language set to: {current_language}[/green]")
                        else:
                            console.print("[red]Supported: python, javascript, bash[/red]")

                    elif cmd == "/clear":
                        agent.history.clear()
                        console.print("[green]History cleared.[/green]")

                    else:
                        console.print(f"[red]Unknown command: {cmd}[/red]")
                        console.print("Type /help for available commands.")

                else:
                    # Regular chat
                    agent.chat(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use /quit to exit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
