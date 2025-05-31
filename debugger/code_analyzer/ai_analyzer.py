import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import google.generativeai as genai

console = Console()

class AIAnalyzer:
    """Analyze Python code for issues like security risks, slow performance, and coding mistakes."""

    def __init__(self):
        """Load your API key and initialize Gemini AI."""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            console.print(
                Panel.fit(
                    "[bold red]❌ Gemini API key not found![/bold red]\n"
                    "📌 Add it to a `.env` file like:\n\n"
                    "[green]GEMINI_API_KEY=your_api_key[/green]",
                    title="Missing API Key"
                )
            )
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            console.print(Panel.fit("✅ Gemini AI is ready!", border_style="green"))
        except Exception as e:
            console.print(
                Panel.fit(
                    f"❌ [bold red]Error:[/bold red] {str(e)}\n"
                    "🔧 Tip: Visit https://makersuite.google.com/app/apikey to manage your key.",
                    title="API Setup Failed"
                )
            )
            self.model = None

    def analyze(self, code: str) -> Dict[str, Any]:
        """Send your code to Gemini AI and get easy-to-understand suggestions."""
        if not self.model:
            return {
                "error": "AI analysis is disabled",
                "fix": "Check your API key in your .env file",
                "suggestions": {cat: [] for cat in ["security", "performance", "best_practices"]}
            }

        try:
            prompt = (
                "Analyze this Python code and return suggestions in these 3 simple sections:\n"
                "1. Security Issues (unsafe code)\n"
                "2. Performance Tips (slow or heavy code)\n"
                "3. Best Practices (clean, professional code)\n\n"
                "Make suggestions short, clear, and beginner-friendly. Start each suggestion with '- ' and group them under section headers.\n\n"
                f"Code:\n{code}"
            )

            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()

            return {
                "suggestions": self._parse_suggestions(analysis_text),
                "raw_analysis": analysis_text
            }

        except Exception as e:
            return {
                "error": "AI failed to analyze code.",
                "fix": str(e),
                "suggestions": {cat: [] for cat in ["security", "performance", "best_practices"]}
            }

    def _parse_suggestions(self, analysis: str) -> Dict[str, List[str]]:
        """Organize Gemini suggestions into categories for clear printing."""
        suggestions = {
            "security": [],
            "performance": [],
            "best_practices": []
        }

        current = "best_practices"

        for line in analysis.splitlines():
            line = line.strip()
            if not line:
                continue

            if "security" in line.lower():
                current = "security"
            elif "performance" in line.lower():
                current = "performance"
            elif "best practice" in line.lower():
                current = "best_practices"
            elif line.startswith("- "):
                suggestions[current].append(line[2:])

        return suggestions


def print_suggestions(result: Dict[str, Any]) -> None:
    """Display suggestions in a friendly, readable format."""
    if "error" in result:
        console.print(
            Panel.fit(
                f"[bold red]{result['error']}[/bold red]\n[yellow]{result['fix']}[/yellow]",
                title="❌ Problem",
                border_style="red"
            )
        )
        return

    suggestions = result["suggestions"]

    if all(not tips for tips in suggestions.values()):
        console.print(
            Panel.fit("✅ Your code looks great! No issues found.", border_style="green")
        )
        return

    # Titles and colors for each section
    categories = {
        "security": ("🔐 Security Warnings", "red", "These are risky parts that could be unsafe."),
        "performance": ("⚡ Performance Tips", "yellow", "Speed up your code and reduce resource use."),
        "best_practices": ("✅ Best Practices", "green", "Make your code cleaner and easier to understand.")
    }

    for cat, tips in suggestions.items():
        if not tips:
            continue

        title, color, subtitle = categories[cat]

        console.print(Panel.fit(f"[bold {color}]{title}[/bold {color}]\n[dim]{subtitle}[/dim]", border_style=color))

        for i, tip in enumerate(tips, 1):
            console.print(f"[{color}]{i}. {tip}[/{color}]")

        console.print()

