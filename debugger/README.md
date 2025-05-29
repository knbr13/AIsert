# Code Analyzer

A Python-based code analysis tool that provides multiple analysis methods for Python code.

## Features

- AST (Abstract Syntax Tree) Analysis
- Pylint Integration
- AI-Powered Code Analysis
- Test API Integration

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - Optional: Configure API settings:
     ```
     API_TIMEOUT=5
     API_MAX_RETRIES=3
     ```

## Usage

Run the main script:
```bash
python main.py [file_to_analyze] [options]
```

Available options:
- `--no-ai-analysis`: Skip AI analysis
- `--no-api-test`: Skip API testing

Examples:
```bash
# Analyze a specific file
python main.py your_file.py

# Skip AI analysis
python main.py your_file.py --no-ai-analysis

# Skip API testing
python main.py your_file.py --no-api-test
```

## Project Structure

- `main.py`: Main entry point
- `code_analyzer/`: Core analysis modules
  - `ast_analyzer.py`: AST-based code analysis
  - `pylint_analyzer.py`: Pylint integration
  - `ai_analyzer.py`: AI-powered analysis
  - `test_api.py`: API testing utilities

## Requirements

See `requirements.txt` for full list of dependencies.

## License

MIT License 