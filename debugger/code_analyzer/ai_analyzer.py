import os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

class AIAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.client = None
            print("❌ Error: No API key found!")
            print("🔧 Fix: Create a .env file and add: GEMINI_API_KEY=your_api_key_here")
            return
            
        try:
            print("Configuring Gemini AI...")
            genai.configure(api_key=api_key)
            
            # Try to get the basic model
            print("\nAttempting to get model...")
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Model successfully initialized!")
            self.client = True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("🔧 Fix: Check if your API key is valid at https://makersuite.google.com/app/apikey")
            self.client = None

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code using Gemini AI.
        
        Args:
            code (str): Python code to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        if not self.client:
            return {
                "error": "❌ AI analysis is disabled",
                "fix": "🔧 Please check your API key and access permissions",
                "suggestions": {
                    "style": [],
                    "performance": [],
                    "security": [],
                    "best_practices": []
                }
            }

        try:
            print("\nGenerating analysis...")
            prompt = f"""Analyze this Python code and provide suggestions for improvement in the following categories:
            - Style
            - Performance
            - Security
            - Best Practices

            Code to analyze:
            {code}

            Please format your response with clear category headers and bullet points for each suggestion."""

            response = self.model.generate_content(prompt)
            analysis = response.text
            print("✅ Analysis generated successfully!")
            
            return {
                "suggestions": self._parse_suggestions(analysis),
                "raw_analysis": analysis
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error: {error_message}")
            
            if "not found" in error_message or "not supported" in error_message:
                return {
                    "error": "❌ API access error",
                    "fix": "🔧 Please ensure you have access to the Gemini model at https://makersuite.google.com/app/apikey",
                    "suggestions": {
                        "style": [],
                        "performance": [],
                        "security": [],
                        "best_practices": []
                    }
                }
            return {
                "error": f"❌ AI analysis failed",
                "fix": f"🔧 {error_message}",
                "suggestions": {
                    "style": [],
                    "performance": [],
                    "security": [],
                    "best_practices": []
                }
            }

    def _parse_suggestions(self, analysis: str) -> Dict[str, Any]:
        """
        Parse the AI analysis into structured suggestions.
        
        Args:
            analysis (str): Raw analysis from AI
            
        Returns:
            Dict[str, Any]: Structured suggestions
        """
        # Simple parsing logic - can be enhanced based on needs
        suggestions = {
            "style": [],
            "performance": [],
            "security": [],
            "best_practices": []
        }
        
        # Basic categorization of suggestions
        lines = analysis.split('\n')
        current_category = "best_practices"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "style" in line.lower():
                current_category = "style"
            elif "performance" in line.lower():
                current_category = "performance"
            elif "security" in line.lower():
                current_category = "security"
            elif line.startswith("- ") or line.startswith("* "):
                suggestions[current_category].append(line[2:])
                
        return suggestions 