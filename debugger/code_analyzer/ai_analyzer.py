import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import google.generativeai as genai

console = Console()

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self._display_missing_key()
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                console.print("[bold green]✅ AI Analyzer initialized successfully.[/bold green]")
            except Exception as e:
                console.print(f"[bold red]❌ Failed to initialize AI: {e}[/bold red]")
                self.model = None

    def _display_missing_key(self):
        console.print("[bold red]❌ Missing API Key![/bold red]")
        console.print("[bold yellow]🔧 Please add this to your .env file: GEMINI_API_KEY=your_key_here[/bold yellow]")

    def analyze(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        if not self.model:
            console.print("[red]❌ AI model is not initialized.[/red]")
            return []

        prompt = f"""
You are a professional {language} code reviewer.
Analyze the following code and return all issues in this strict format:

- Type: [Security Issue, Performance Issue, Best Practice]
- Line: [line number or 'Multiple']
- Description: [brief description]
- Why: [why it's a problem]
- Fix: [suggest code fix]
- Best Practice: [how to prevent it in the future]

Respond in plain text with the exact format for each issue. No markdown or extra text.

Here is the {language} code:
\"\"\"{language}
{code}
\"\"\"
"""

        try:
            response = self.model.generate_content(prompt)
            raw_output = response.text.strip()
            console.print(Panel.fit(Syntax(code, language, theme="monokai", line_numbers=True), title=f"Analyzed {language.capitalize()} Code"))

            issues = self._parse_ai_output(raw_output)

            if not issues:
                console.print("[yellow]⚠️ Could not parse issues. Showing raw output:[/yellow]")
                console.print(raw_output)
                return [{
                    "type": "Unknown",
                    "line": "N/A",
                    "description": raw_output,
                    "why": "",
                    "fix": "",
                    "best_practice": ""
                }]

            return issues

        except Exception as e:
            console.print(f"[bold red]❌ Error during analysis: {e}[/bold red]")
            return []

    def _parse_ai_output(self, output: str) -> List[Dict[str, Any]]:
        issues = []
        current = {}

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith("- Type:"):
                if current:
                    issues.append(current)
                current = {
                    "type": line.replace("- Type:", "").strip(),
                    "line": "",
                    "description": "",
                    "why": "",
                    "fix": "",
                    "best_practice": ""
                }
            elif line.startswith("- Line:"):
                current["line"] = line.replace("- Line:", "").strip()
            elif line.startswith("- Description:"):
                current["description"] = line.replace("- Description:", "").strip()
            elif line.startswith("- Why:"):
                current["why"] = line.replace("- Why:", "").strip()
            elif line.startswith("- Fix:"):
                current["fix"] = line.replace("- Fix:", "").strip()
            elif line.startswith("- Best Practice:"):
                current["best_practice"] = line.replace("- Best Practice:", "").strip()

        if current:
            issues.append(current)

        return issues


def print_ai_results(issues: List[Dict[str, Any]]) -> None:
    if not issues:
        console.print("[bold green]✅ No issues found! Your code looks good![/bold green]")
        return

    table = Table(title="AI Code Review Results", header_style="bold magenta")

    table.add_column("Type", style="red", no_wrap=True)
    table.add_column("Line", style="cyan")
    table.add_column("Description", style="yellow")
    table.add_column("Why", style="green")
    table.add_column("Fix", style="white")
    table.add_column("Best Practice", style="blue")

    for issue in issues:
        table.add_row(
            issue["type"],
            issue["line"],
            issue["description"],
            issue["why"],
            issue["fix"],
            issue["best_practice"]
        )

    console.print(table)
