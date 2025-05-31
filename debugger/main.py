import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from code_analyzer.ai_analyzer import AIAnalyzer
from code_analyzer.error_checker import GeminiCodeChecker, print_analysis
from code_analyzer.generate_requirements import generate_requirements

# Initialize colorama and rich console for colored output
init()
console = Console()


# ----------------------------
# Argument Parsing
# ----------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Code Analyzer - Python code quality tool')
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to a Python file or directory to analyze'
    )
    parser.add_argument(
        '--no-ai-analysis',
        action='store_true',
        help='Skip AI analysis'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=7.0,
        help='Minimum acceptable score (not used in current version)'
    )
    return parser.parse_args()


# ----------------------------
# File Loading
# ----------------------------

def load_code_from_path(path_str: str) -> str:
    """
    Load Python code from the given file or directory path.
    If a directory is given, recursively load all `.py` files excluding 'venv' and '__pycache__'.
    """
    path = Path(path_str)

    if not path.exists():
        print(f"{Fore.RED}Error: Path '{path}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)

    code_chunks: List[str] = []

    if path.is_dir():
        for file_path in path.rglob("*.py"):
            if "venv" in file_path.parts or "__pycache__" in file_path.parts:
                continue
            try:
                with file_path.open(encoding="utf-8") as f:
                    code_chunks.append(f"# File: {file_path}\n{f.read()}\n")
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not read {file_path}: {e}{Style.RESET_ALL}")
    else:
        try:
            with path.open(encoding="utf-8") as f:
                code_chunks.append(f.read())
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied reading '{path}'.{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Error reading '{path}': {e}{Style.RESET_ALL}")
            sys.exit(1)

    return "\n".join(code_chunks) if code_chunks else ""


# ----------------------------
# Output Formatting Helpers
# ----------------------------

def print_header(title: str) -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 20} {title} {'=' * 20}{Style.RESET_ALL}")

def print_section(title: str) -> None:
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{title}:{Style.RESET_ALL}")

def print_ai_results(results: Dict[str, Any]) -> None:
    print_header("AI Analysis")
    if "error" in results:
        console.print(
            Panel.fit(
                f"[bold red]{results['error']}[/bold red]\n[bold yellow]{results.get('fix', '')}[/bold yellow]",
                title="❌ AI Analysis Failed",
                style="red",
            )
        )
        return

    suggestions = results.get("suggestions", {})
    if not any(suggestions.values()):
        console.print("[bold green]✅ No issues found! Your code looks clean![/bold green]")
        return

    console.print(Panel.fit("[bold blue]🔐 Always Watching, Always Securing[/bold blue]", style="cyan"))

    for category, tips in suggestions.items():
        if not tips:
            continue
        table = Table(title=category.replace("_", " ").title(), header_style="bold magenta", show_lines=True)
        table.add_column("Suggestions", style="yellow")
        for tip in tips:
            table.add_row(tip)
        console.print(table)

def print_requirements_results(target_dir: str) -> None:
    print_header("Requirements Generation")
    print(f"\n{Fore.YELLOW}Generating requirements for: {target_dir}{Style.RESET_ALL}")
    generate_requirements(target_dir)


# ----------------------------
# Main Program Logic
# ----------------------------

def main() -> None:
    load_dotenv()
    args = parse_arguments()

    # Load code or use sample if no path provided
    if args.path:
        code = load_code_from_path(args.path)
    else:
        code = """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"The sum is: {result}")
"""

    analyzed_path = args.path if args.path else "Example code"
    print(f"\n{Fore.CYAN}Analyzing: {Fore.YELLOW}{analyzed_path}{Style.RESET_ALL}")

    # Initialize analyzers
    ai_analyzer = AIAnalyzer()
    error_checker = GeminiCodeChecker()

    analysis_options = {
        1: ("Error Checker", lambda: print_analysis(error_checker.analyze_code(code))),
        2: ("AI Analysis", lambda: print_ai_results(ai_analyzer.analyze(code)) if not args.no_ai_analysis else print(f"{Fore.YELLOW}AI Analysis skipped.{Style.RESET_ALL}")),
        3: ("Generate Requirements", lambda: print_requirements_results(os.path.dirname(args.path) if args.path else os.getcwd())),
    }

    # Display menu
    print(f"\n{Fore.CYAN}Available Analysis Tools:{Style.RESET_ALL}")
    for num, (name, _) in analysis_options.items():
        print(f"{Fore.YELLOW}{num}.{Style.RESET_ALL} {name}")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Run All Analyses")
    print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Exit")

    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Select an option (0-4): {Style.RESET_ALL}").strip()
            if choice == '0':
                print(f"{Fore.GREEN}Exiting. Goodbye!{Style.RESET_ALL}")
                break

            if choice == '4':
                # Run all analyses
                for num in sorted(analysis_options.keys()):
                    print(f"\n{Fore.MAGENTA}>>> Running: {analysis_options[num][0]} <<<{Style.RESET_ALL}")
                    analysis_options[num][1]()
                continue

            option = int(choice)
            if option in analysis_options:
                print(f"\n{Fore.MAGENTA}>>> Running: {analysis_options[option][0]} <<<{Style.RESET_ALL}")
                analysis_options[option][1]()
            else:
                print(f"{Fore.RED}Invalid option. Please choose a number between 0 and 4.{Style.RESET_ALL}")

        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number between 0 and 4.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Interrupted by user. Exiting...{Style.RESET_ALL}")
            break


if __name__ == "__main__":
    main()
