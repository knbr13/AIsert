import ast
from typing import Dict, List, Any

class ASTAnalyzer:
    def __init__(self):
        self.analysis_results = {}

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code using AST.
        
        Args:
            code (str): Python code to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            tree = ast.parse(code)
            self.analysis_results = {
                "functions": self._analyze_functions(tree),
                "classes": self._analyze_classes(tree),
                "imports": self._analyze_imports(tree),
                "complexity": self._analyze_complexity(tree)
            }
            return self.analysis_results
        except SyntaxError as e:
            return {"error": str(e)}

    def _analyze_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "returns": isinstance(node.returns, ast.Name) and node.returns.id or None
                })
        return functions

    def _analyze_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
        return classes

    def _analyze_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{node.names[0].name}")
        return imports

    def _analyze_complexity(self, tree: ast.AST) -> Dict[str, int]:
        complexity = {
            "functions": 0,
            "classes": 0,
            "loops": 0,
            "conditionals": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                complexity["loops"] += 1
            elif isinstance(node, ast.If):
                complexity["conditionals"] += 1
                
        return complexity 