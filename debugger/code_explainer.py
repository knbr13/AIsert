import os
import sys
import ast
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    total_lines: int
    function_count: int
    class_count: int
    import_count: int
    variable_count: int
    complexity: int
    docstring_count: int
    comment_count: int

class CodeExplainer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the code explainer with optional API key."""
        self.api_key = api_key or "AIzaSyB6oEIrQc-a504MyWFlPZCgmbhy93yKfhw"
        self.client = None
        self.model = None
        self._initialize_ai()

    def _initialize_ai(self) -> None:
        """Initialize the AI model."""
        try:
            print("Initializing AI model...")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.0-pro')
            self.client = True
            print("AI model initialized successfully!")
        except Exception as e:
            print(f"Error initializing AI model: {str(e)}")
            self.client = None

    def analyze_file(self, file_path: str, output_format: str = "text") -> Dict[str, Any]:
        """
        Analyze a Python file and generate a detailed report.
        
        Args:
            file_path: Path to the Python file
            output_format: Output format (text, json, html, md)
            
        Returns:
            Dictionary containing the analysis results
        """
        if not self.client:
            return self._create_error_response("AI model not initialized")

        try:
            # Read and analyze the file
            code = self._read_file(file_path)
            metrics = self._analyze_metrics(code)
            explanation = self._get_ai_explanation(code)
            
            # Create the report
            report = {
                "file_info": self._get_file_info(file_path),
                "metrics": metrics.__dict__,
                "explanation": explanation,
                "sections": self._parse_explanation(explanation)
            }
            
            # Generate output in requested format
            return self._format_output(report, output_format)
            
        except FileNotFoundError:
            return self._create_error_response(f"File not found: {file_path}")
        except Exception as e:
            return self._create_error_response(f"Analysis error: {str(e)}")

    def _read_file(self, file_path: str) -> str:
        """Read a file and return its contents."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _analyze_metrics(self, code: str) -> CodeMetrics:
        """Analyze code metrics using AST."""
        try:
            tree = ast.parse(code)
            lines = code.splitlines()
            
            return CodeMetrics(
                total_lines=len(lines),
                function_count=len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                class_count=len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                import_count=len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]),
                variable_count=len([node for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)]),
                complexity=self._calculate_complexity(tree),
                docstring_count=len([node for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)]),
                comment_count=sum(1 for line in lines if line.strip().startswith('#'))
            )
        except:
            return CodeMetrics(0, 0, 0, 0, 0, 0, 0, 0)

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.FunctionDef, ast.ClassDef)):
                complexity += 1
        return complexity

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information."""
        path = Path(file_path)
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": path.stat().st_size,
            "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "analysis_date": datetime.now().isoformat()
        }

    def _get_ai_explanation(self, code: str) -> str:
        """Get AI explanation of the code."""
        prompt = f"""Analyze this Python code and provide a detailed explanation covering:
        1. Overall Purpose
        2. Key Components
        3. Function/Class Explanations
        4. Important Variables and Data Structures
        5. Control Flow
        6. Best Practices Used
        7. Potential Improvements
        8. Security Considerations
        9. Performance Analysis
        10. Testing Recommendations

        Code to analyze:
        {code}

        Please format your response with clear section headers and bullet points."""

        response = self.model.generate_content(prompt)
        return response.text

    def _parse_explanation(self, explanation: str) -> Dict[str, str]:
        """Parse the AI explanation into sections."""
        sections = {
            "Overall Purpose": "",
            "Key Components": "",
            "Function/Class Explanations": "",
            "Important Variables": "",
            "Control Flow": "",
            "Best Practices": "",
            "Improvements": "",
            "Security Considerations": "",
            "Performance Analysis": "",
            "Testing Recommendations": ""
        }
        
        current_section = None
        current_content = []
        
        for line in explanation.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            for section in sections.keys():
                if section.lower() in line.lower():
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section
                    current_content = []
                    break
            else:
                if current_section:
                    current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def _format_output(self, report: Dict[str, Any], format: str) -> Dict[str, Any]:
        """Format the report in the requested output format."""
        if format == "json":
            return {"format": "json", "content": json.dumps(report, indent=2)}
        elif format == "html":
            return {"format": "html", "content": self._generate_html(report)}
        elif format == "md":
            return {"format": "markdown", "content": self._generate_markdown(report)}
        else:
            return report

    def _generate_html(self, report: Dict[str, Any]) -> str:
        """Generate HTML report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Analysis - {report['file_info']['name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric {{ padding: 15px; background: #f5f5f5; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric strong {{ color: #2c3e50; }}
                h1, h2 {{ color: #2c3e50; }}
                .file-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Code Analysis Report</h1>
                
                <div class="file-info">
                    <h2>File Information</h2>
                    <p><strong>Name:</strong> {report['file_info']['name']}</p>
                    <p><strong>Path:</strong> {report['file_info']['path']}</p>
                    <p><strong>Size:</strong> {report['file_info']['size']} bytes</p>
                    <p><strong>Last Modified:</strong> {report['file_info']['last_modified']}</p>
                    <p><strong>Analysis Date:</strong> {report['file_info']['analysis_date']}</p>
                </div>

                <div class="section">
                    <h2>Code Metrics</h2>
                    <div class="metrics">
        """
        
        for key, value in report['metrics'].items():
            html += f'<div class="metric"><strong>{key}:</strong> {value}</div>'
        
        html += """
                    </div>
                </div>
        """
        
        for section, content in report['sections'].items():
            if content:
                html += f"""
                <div class="section">
                    <h2>{section}</h2>
                    <div>{content}</div>
                </div>
                """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        md = f"# Code Analysis Report\n\n"
        
        # File Information
        md += "## File Information\n"
        md += f"- **Name:** {report['file_info']['name']}\n"
        md += f"- **Path:** {report['file_info']['path']}\n"
        md += f"- **Size:** {report['file_info']['size']} bytes\n"
        md += f"- **Last Modified:** {report['file_info']['last_modified']}\n"
        md += f"- **Analysis Date:** {report['file_info']['analysis_date']}\n\n"
        
        # Metrics
        md += "## Code Metrics\n"
        for key, value in report['metrics'].items():
            md += f"- **{key}:** {value}\n"
        
        # Sections
        md += "\n## Detailed Analysis\n"
        for section, content in report['sections'].items():
            if content:
                md += f"\n### {section}\n{content}\n"
        
        return md

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "error": message,
            "explanation": message,
            "sections": {},
            "metrics": {},
            "file_info": {}
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python code_explainer.py <python_file> [output_format]")
        print("Output formats: text (default), json, html, md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "text"
    
    explainer = CodeExplainer()
    results = explainer.analyze_file(file_path, output_format)
    
    if output_format == "json":
        print(results["content"])
    elif output_format == "html":
        output_file = "analysis_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(results["content"])
        print(f"HTML report generated: {output_file}")
    elif output_format == "md":
        output_file = "analysis_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(results["content"])
        print(f"Markdown report generated: {output_file}")
    else:
        # Print file info
        print("\n==================== File Information ====================\n")
        for key, value in results["file_info"].items():
            print(f"{key}: {value}")
        
        # Print metrics
        print("\n==================== Code Metrics ====================\n")
        for key, value in results["metrics"].items():
            print(f"{key}: {value}")
        
        # Print explanation
        print("\n==================== Code Explanation ====================\n")
        print(results["explanation"])
        
        # Print sections
        print("\n==================== Detailed Sections ====================\n")
        for section, content in results["sections"].items():
            if content:
                print(f"\n{section}:")
                print(content)

if __name__ == "__main__":
    main() 