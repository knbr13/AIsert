import os
import sys
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from colorama import init, Fore, Style
from code_analyzer.ast_analyzer import ASTAnalyzer
from code_analyzer.pylint_analyzer import PylintAnalyzer
from code_analyzer.ai_analyzer import AIAnalyzer
from code_analyzer.test_api import TestAPI
from code_analyzer.error_checker import GeminiCodeChecker, print_analysis

# Initialize colorama for cross-platform colored output
init()

# ============================================================================
# Command Line Interface
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the code analyzer."""
    parser = argparse.ArgumentParser(
        description='Code Analyzer - A tool for analyzing Python code quality'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Python file to analyze (optional)'
    )
    parser.add_argument(
        '--no-ai-analysis',
        action='store_true',
        help='Skip AI analysis'
    )
    parser.add_argument(
        '--no-api-test',
        action='store_true',
        help='Skip API testing'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=7.0,
        help='Minimum acceptable Pylint score (default: 7.0)'
    )
    return parser.parse_args()

# ============================================================================
# File Operations
# ============================================================================

def load_code(file_path: str) -> str:
    """Load code from a file with proper error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File '{file_path}' not found.{Style.RESET_ALL}")
        sys.exit(1)
    except PermissionError:
        print(f"{Fore.RED}Error: Permission denied when reading '{file_path}'.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
        sys.exit(1)

# ============================================================================
# Output Formatting
# ============================================================================

def print_header(title: str) -> None:
    """Print a colored section header with consistent formatting."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 20} {title} {'=' * 20}{Style.RESET_ALL}")

def print_section(title: str) -> None:
    """Print a colored section title."""
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{title}:{Style.RESET_ALL}")

def print_ast_results(results: Dict[str, Any]) -> None:
    """Print AST analysis results with clear formatting."""
    print_header("AST Analysis")
    
    if "functions" in results:
        print_section("Functions")
        for func in results["functions"]:
            args = ", ".join(func["args"]) if func["args"] else "no args"
            print(f"  • {Fore.YELLOW}{func['name']}{Style.RESET_ALL}({args})")
    
    if "imports" in results and results["imports"]:
        print_section("Imports")
        for imp in results["imports"]:
            print(f"  • {Fore.YELLOW}{imp}{Style.RESET_ALL}")

def print_pylint_results(results: Dict[str, Any]) -> None:
    """Print Pylint analysis results with clear formatting."""
    print_header("Pylint Analysis")
    
    if "error" in results:
        print(f"\n{Fore.RED}✗ Error: {results['error']}{Style.RESET_ALL}")
        return
        
    # Print score
    score_color = Fore.GREEN if results["score"] >= 7.0 else Fore.RED
    print(f"\nScore: {score_color}{results['score']:.1f}/10.0{Style.RESET_ALL}")
    
    # Print issues if any
    if results["issues"]:
        print_section("Issues Found")
        for issue in results["issues"]:
            print(f"  {Fore.YELLOW}{issue}{Style.RESET_ALL}")
    
    # Print scoring details
    if "scoring_details" in results:
        print_section("Score Breakdown")
        details = results["scoring_details"]
        print(f"  Starting Score: {details['base_score']}")
        print(f"  Critical Issues: -{details['critical_issues']:.2f}")
        print(f"  Style Issues: -{details['style_issues']:.2f}")
        print(f"  Repeated Issues: -{details['repeated_issues']:.2f}")
    
    print(f"\nTotal Issues: {results['total_issues']}")

def print_ai_results(results: Dict[str, Any]) -> None:
    """Print AI analysis results with clear formatting."""
    print_header("AI Analysis")
    
    if "suggestions" in results:
        for category, suggestions in results["suggestions"].items():
            if suggestions:
                print_section(f"{category.title()} Suggestions")
                for suggestion in suggestions:
                    print(f"  • {Fore.YELLOW}{suggestion}{Style.RESET_ALL}")

def print_api_results(results: Dict[str, Any]) -> None:
    """Print API test results with clear formatting."""
    print_header("API Test")
    
    if "error" in results:
        print(f"\n{Fore.RED}✗ Error: {results['error']}{Style.RESET_ALL}")
    else:
        status_color = Fore.GREEN if results["status"] == 200 else Fore.RED
        print_section("Response")
        print(f"  Status: {status_color}{results['status']}{Style.RESET_ALL}")
        print(f"  Time: {Fore.YELLOW}{results['elapsed_time']:.2f}s{Style.RESET_ALL}")

# ============================================================================
# Main Program
# ============================================================================

def main():
    """Main entry point for the code analyzer."""
    # Parse arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize analyzers
    ast_analyzer = ASTAnalyzer()
    pylint_analyzer = PylintAnalyzer()
    ai_analyzer = AIAnalyzer()
    test_api = TestAPI()
    error_checker = GeminiCodeChecker()
    
    # Get code to analyze
    code = load_code(args.file) if args.file else """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"The sum is: {result}")
    """
    
    # Print file being analyzed
    print(f"\n{Fore.CYAN}Analyzing: {Fore.YELLOW}{args.file if args.file else 'Example code'}{Style.RESET_ALL}")
    
    # Show analysis menu and get user choice
    print(f"\n{Fore.CYAN}Available Analysis Tools:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Error Checker")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} AST Analysis")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Pylint Analysis")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} AI Analysis")
    print(f"{Fore.YELLOW}5.{Style.RESET_ALL} API Tests")
    print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Run All Analyses")
    print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Exit")
    
    while True:
        try:
            choice = input(f"\n{Fore.GREEN}Select analysis tools (comma-separated numbers, e.g., 1,3,4): {Style.RESET_ALL}")
            if choice.strip() == "0":
                sys.exit(0)
                
            selected = [int(x.strip()) for x in choice.split(",")]
            valid_choices = []
            
            for num in selected:
                if 1 <= num <= 6:
                    valid_choices.append(num)
                else:
                    print(f"{Fore.RED}Invalid choice: {num}. Please select numbers between 1 and 6.{Style.RESET_ALL}")
            
            if not valid_choices:
                print(f"{Fore.RED}No valid choices selected. Please try again.{Style.RESET_ALL}")
                continue
            
            # Run selected analyses
            if 6 in valid_choices:  # Run All
                valid_choices = [1, 2, 3, 4, 5]
            
            for choice in valid_choices:
                if choice == 1:  # Error Checker
                    print(f"\n{Fore.YELLOW}Running Error Checker...{Style.RESET_ALL}")
                    error_issues = error_checker.analyze_code(code)
                    print_analysis(error_issues)
                elif choice == 2:  # AST Analysis
                    print(f"\n{Fore.YELLOW}Running AST Analysis...{Style.RESET_ALL}")
                    ast_results = ast_analyzer.analyze(code)
                    print_ast_results(ast_results)
                elif choice == 3:  # Pylint Analysis
                    print(f"\n{Fore.YELLOW}Running Pylint Analysis...{Style.RESET_ALL}")
                    pylint_results = pylint_analyzer.analyze(code)
                    print_pylint_results(pylint_results)
                elif choice == 4:  # AI Analysis
                    print(f"\n{Fore.YELLOW}Running AI Analysis...{Style.RESET_ALL}")
                    ai_results = ai_analyzer.analyze(code)
                    print_ai_results(ai_results)
                elif choice == 5:  # API Tests
                    print(f"\n{Fore.YELLOW}Running API Tests...{Style.RESET_ALL}")
                    api_results = test_api.test_endpoint("https://api.github.com/zen")
                    print_api_results(api_results)
            
            break  # Exit the loop after running analyses
            
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter comma-separated numbers.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Analysis interrupted by user.{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}Error during analysis: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)

if __name__ == "__main__":
    main() 