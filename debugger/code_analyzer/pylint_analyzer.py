import os
import tempfile
from typing import Dict, Any, List
from pylint import lint
from pylint.reporters import JSONReporter

class PylintAnalyzer:
    def __init__(self):
        self.reporter = JSONReporter()
        # Renamed weights to be more descriptive
        self.issue_weights = {
            'error': 0.8,      # Critical issues
            'warning': 0.5,    # Important issues
            'convention': 0.2, # Style issues
            'refactor': 0.3,   # Code structure issues
            'fatal': 0.8       # Critical issues
        }
        # Renamed type weights to be more descriptive
        self.category_weights = {
            'C': 0.2,  # Style issues
            'R': 0.3,  # Code structure
            'W': 0.4,  # Important warnings
            'E': 0.6,  # Errors
            'F': 0.8   # Critical errors
        }

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code using Pylint.
        
        Args:
            code (str): Python code to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Create a temporary file to store the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Run pylint on the temporary file
            lint.Run([temp_file_path], reporter=self.reporter, exit=False)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Process the results
            results = self._process_results()
            return results
            
        except Exception as e:
            return {"error": str(e)}

    def _process_results(self) -> Dict[str, Any]:
        """
        Process the Pylint results into a more usable format with enhanced scoring.
        
        Returns:
            Dict[str, Any]: Processed results with detailed scoring
        """
        messages = self.reporter.messages
        
        # Initialize scoring components
        base_score = 10.0
        critical_issues_penalty = 0.0
        style_issues_penalty = 0.0
        repeated_issues_penalty = 0.0
        
        # Track issue frequencies for frequency-based penalties
        issue_frequencies = {}
        
        # Format issues in a simpler line-by-line format
        formatted_issues = []
        for msg in messages:
            # Get message attributes safely
            msg_type = getattr(msg, 'type', 'convention')
            msg_symbol = getattr(msg, 'symbol', '')
            msg_msg = getattr(msg, 'msg', '')
            msg_line = getattr(msg, 'line', 0)
            msg_column = getattr(msg, 'column', 0)
            
            # Calculate penalties
            issue_weight = self.issue_weights.get(msg_type, 0.3)
            category_weight = self.category_weights.get(msg_symbol[0] if msg_symbol else 'C', 0.3)
            
            # Update frequency tracking
            issue_key = f"{msg_type}:{msg_symbol}"
            issue_frequencies[issue_key] = issue_frequencies.get(issue_key, 0) + 1
            
            # Calculate penalties
            critical_issues_penalty += issue_weight * 0.08
            style_issues_penalty += category_weight * 0.08
            
            # Format issue in a simple line format
            formatted_issue = f"Line {msg_line}: [{msg_type.upper()}] {msg_msg}"
            formatted_issues.append(formatted_issue)
        
        # Calculate repeated issues penalty
        for frequency in issue_frequencies.values():
            repeated_issues_penalty += (frequency - 1) * 0.03
        
        # Calculate final score
        final_score = base_score - (critical_issues_penalty + style_issues_penalty + repeated_issues_penalty)
        final_score = max(0.0, min(10.0, final_score + 0.5))
        
        return {
            "score": round(final_score, 2),
            "issues": formatted_issues,
            "total_issues": len(formatted_issues),
            "scoring_details": {
                "base_score": base_score,
                "critical_issues": round(critical_issues_penalty, 2),
                "style_issues": round(style_issues_penalty, 2),
                "repeated_issues": round(repeated_issues_penalty, 2)
            }
        } 