# Imports
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Custom analyzers
from code_analyzer.ai_analyzer import AIAnalyzer
from code_analyzer.error_checker import GeminiCodeChecker, print_analysis
from code_analyzer.generate_requirements import generate_requirements

# Initialize colorama and rich console for better UI
init()
console = Console()

def parse_args():
    """Get path of code to analyze"""
    parser = argparse.ArgumentParser(description='Python Code Analyzer')
    parser.add_argument('path', nargs='?', help='Python file or directory to analyze')
    return parser.parse_args()

def load_code(path_str):
    path = Path(path_str)
    if not path.exists():
        print(f"{Fore.RED}Error: Path '{path}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)

    codes = []
    if path.is_dir():
        # If path is a directory, load all Python files recursively
        for file in path.rglob('*.py'):
            if 'venv' in file.parts or '__pycache__' in file.parts:
                continue
            try:
                with file.open(encoding='utf-8') as f:
                    codes.append(f"# File: {file}\n{f.read()}\n")
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not read {file}: {e}{Style.RESET_ALL}")
    else:
        # If path is a single file, load it directly
        try:
            with path.open(encoding='utf-8') as f:
                codes.append(f.read())
        except Exception as e:
            print(f"{Fore.RED}Error reading '{path}': {e}{Style.RESET_ALL}")
            sys.exit(1)

    return "\n".join(codes)

def print_ai_results(issues):
    """Display analysis results in table format"""
    if not issues:
        console.print("[bold green]✅ No issues found! Your code looks clean![/bold green]")
        return

    table = Table(title="AI Code Review Results", header_style="bold magenta")

    table.add_column("Type", style="red", no_wrap=True)
    table.add_column("Line", style="cyan")
    table.add_column("Description", style="yellow")
    table.add_column("Why", style="green")
    table.add_column("Fix", style="white")
    table.add_column("Best Practice", style="blue")

    # Add each issue to the table
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

def main():
    load_dotenv()
    args = parse_args()

    # Load the code to analyze
    if args.path:
        code = load_code(args.path)
    else:
        code = None

    print(f"\n{Fore.CYAN}Analyzing: {Fore.YELLOW}{args.path or 'Example code'}{Style.RESET_ALL}")

    # Initialize analyzers
    ai_analyzer = AIAnalyzer()
    error_checker = GeminiCodeChecker()

    # Define available analysis options with descriptions
    actions = {
        1: ("Error Checker 🔍", lambda: print_analysis(error_checker.analyze_code(code)), "Find those pesky bugs before they find you!"),
        2: ("Security Analysis 🛡️", lambda: print_ai_results(ai_analyzer.analyze(code)), "Fortify your code against digital invaders!"),
        3: ("Generate Requirements 📦", lambda: generate_requirements(os.path.dirname(args.path) if args.path else os.getcwd()), "Never miss a dependency again!")
    }

    # Display menu options
    print(f"\n{Fore.CYAN}Available Analyses:{Style.RESET_ALL}")
    for num, (name, _, description) in actions.items():
        print(f"{Fore.YELLOW}{num}.{Style.RESET_ALL} {name} - {description}")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Run All")
    print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Exit")

    # Main program loop
    while True:
        choice = input(f"\n{Fore.CYAN}Choose (0-4): {Style.RESET_ALL}").strip()
        if choice == '0':
            print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
            break
        elif choice == '4':
            # Run all analyses
            for num in sorted(actions):
                print(f"\n{Fore.MAGENTA}>>> {actions[num][0]} <<< {Style.RESET_ALL}")
                actions[num][1]()
        else:
            try:
                # Run selected analysis
                option = int(choice)
                if option in actions:
                    print(f"\n{Fore.MAGENTA}>>> {actions[option][0]} <<< {Style.RESET_ALL}")
                    actions[option][1]()
                else:
                    print(f"{Fore.RED}Invalid option. Choose 0-4.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number (0-4).{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.GREEN}Interrupted. Exiting...{Style.RESET_ALL}")
                break

if __name__ == "__main__":
    main()
