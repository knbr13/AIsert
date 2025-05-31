import os
import re
import sys
import json
import requests
from pathlib import Path


LANGUAGE_PATTERNS = {
    'python': {
        'extensions': ['.py'],
        'import_patterns': [
            r'^import\s+([a-zA-Z0-9_\.]+)',  
            r'^from\s+([a-zA-Z0-9_\.]+)\s+import', 
        ],
        'stdlib_check': lambda name: (
            name in sys.stdlib_module_names or
            name in sys.builtin_module_names or
            name.startswith('_') or
            name in ['test', 'unittest', 'distutils', 'setuptools', 'pip']
        )
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.ts', '.tsx'],

        'import_patterns': [
            r'^import\s+.*?from\s+[\'"]([^/\'"][^\'"]*)[\'"]',
            r'^const\s+.*?=\s+require\([\'"]([^/\'"][^\'"]*)[\'"]\)',
        ],
        #  built-in modules
        'stdlib_check': lambda name: name in [
             'fs', 'path', 'http', 'https', 'url', 'util', 'events', 'stream',
             'crypto', 'zlib', 'buffer', 'child_process', 'cluster', 'dgram',
             'dns', 'domain', 'os', 'net', 'readline', 'repl', 'tls', 'tty',
             'vm', 'assert', 'constants', 'module', 'process', 'querystring',
             'string_decoder', 'timers', 'v8', 'punycode'
         ]
    },
    'java': {
        'extensions': ['.java'],
        'import_patterns': [r'^import\s+([a-zA-Z0-9_\.]+);'],

        'stdlib_check': lambda name: name.startswith('java.') or name.startswith('javax.')
    },
    'csharp': {
        'extensions': ['.cs'],
        
        'import_patterns': [r'^using\s+([a-zA-Z0-9_\.]+);'], # Matches 'using System.Namespace;'

        #  C# standard library
        'stdlib_check': lambda name: name.startswith('System.') or name.startswith('Microsoft.')
    }
}

# PACKAGE_MAP = A dictionary for correcting package names before searching.
PACKAGE_MAP = {
    'python': {
        'dotenv': 'python-dotenv',
        'sklearn': 'scikit-learn',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'tensorflow': 'tensorflow',
        'torch': 'torch',
        'keras': 'keras',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'requests': 'requests',
        'beautifulsoup4': 'beautifulsoup4',
        'bs4': 'beautifulsoup4',
        'flask': 'flask',
        'django': 'django',
        'fastapi': 'fastapi',
        'sqlalchemy': 'sqlalchemy',
        'pymongo': 'pymongo',
        'redis': 'redis',
        'celery': 'celery',
        'pytest': 'pytest',
        'unittest': 'unittest2',
        'rich': 'rich',
        'colorama': 'colorama',
        'tqdm': 'tqdm',
        'jupyter': 'jupyter',
        'ipython': 'ipython',
        'pylint': 'pylint',
        'black': 'black',
        'flake8': 'flake8',
        'mypy': 'mypy',
        'sphinx': 'sphinx',
        'twine': 'twine',
        'setuptools': 'setuptools',
        'wheel': 'wheel',
        'pip': 'pip',
        'virtualenv': 'virtualenv',
        'conda': 'conda',
        'poetry': 'poetry',
        'pydantic': 'pydantic',
        'typing': 'typing-extensions',
        'cryptography': 'cryptography',
        'pyjwt': 'PyJWT',
        'passlib': 'passlib',
        'bcrypt': 'bcrypt',
        'aiohttp': 'aiohttp',
        'websockets': 'websockets',
        'grpcio': 'grpcio',
        'protobuf': 'protobuf',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'statsmodels': 'statsmodels',
        'plotly': 'plotly',
        'bokeh': 'bokeh',
        'dash': 'dash',
        'streamlit': 'streamlit',
        'gradio': 'gradio',
        'transformers': 'transformers',
        'spacy': 'spacy',
        'nltk': 'nltk',
        'gensim': 'gensim',
        'textblob': 'textblob',
        'pytesseract': 'pytesseract',
        'opencv': 'opencv-python',
        'pillow': 'Pillow',
        'moviepy': 'moviepy',
        'pydub': 'pydub',
        'soundfile': 'soundfile',
        'librosa': 'librosa',
        'pyaudio': 'PyAudio',
        'pygame': 'pygame',
        'pyglet': 'pyglet',
        'arcade': 'arcade',
        'pyopengl': 'PyOpenGL',
        'pygobject': 'PyGObject',
        'pyqt5': 'PyQt5',
        'pyqt6': 'PyQt6',
        'pyside2': 'PySide2',
        'pyside6': 'PySide6',
        'tkinter': 'python-tk',
        'wx': 'wxPython',
        'kivy': 'kivy',
        'pygame': 'pygame',
        'pyglet': 'pyglet',
        'arcade': 'arcade',
        'pyopengl': 'PyOpenGL',
        'pygobject': 'PyGObject',
        'pyqt5': 'PyQt5',
        'pyqt6': 'PyQt6',
        'pyside2': 'PySide2',
        'pyside6': 'PySide6',
        'tkinter': 'python-tk',
        'wx': 'wxPython',
        'kivy': 'kivy'
    },
    'javascript': {
        'react': '@types/react',
        'react-dom': '@types/react-dom',
        'vue': 'vue',
        'angular': '@angular/core',
        'express': 'express',
        'next': 'next',
        'nuxt': 'nuxt',
        'gatsby': 'gatsby',
        'jquery': 'jquery',
        'lodash': 'lodash',
        'moment': 'moment',
        'axios': 'axios',
        'redux': 'redux',
        'mobx': 'mobx',
        'graphql': 'graphql',
        'apollo': 'apollo-client',
        'socket.io': 'socket.io',
        'ws': 'ws',
        'mongoose': 'mongoose',
        'sequelize': 'sequelize',
        'typeorm': 'typeorm',
        'prisma': 'prisma',
        'jest': 'jest',
        'mocha': 'mocha',
        'chai': 'chai',
        'cypress': 'cypress',
        'puppeteer': 'puppeteer',
        'playwright': 'playwright',
        'webpack': 'webpack',
        'babel': '@babel/core',
        'typescript': 'typescript',
        'eslint': 'eslint',
        'prettier': 'prettier',
        'tailwindcss': 'tailwindcss',
        'bootstrap': 'bootstrap',
        'material-ui': '@mui/material',
        'antd': 'antd',
        'styled-components': 'styled-components',
        'sass': 'sass',
        'less': 'less',
        'postcss': 'postcss',
        'autoprefixer': 'autoprefixer',
        'esbuild': 'esbuild',
        'vite': 'vite',
        'rollup': 'rollup',
        'parcel': 'parcel',
        'browserify': 'browserify',
        'gulp': 'gulp',
        'grunt': 'grunt',
        'yarn': 'yarn',
        'npm': 'npm',
        'pnpm': 'pnpm',
        'lerna': 'lerna',
        'nx': 'nx',
        'turborepo': 'turborepo',
        'storybook': 'storybook',
        'docusaurus': 'docusaurus',
        'gatsby': 'gatsby',
        'next': 'next',
        'nuxt': 'nuxt',
        'svelte': 'svelte',
        'sveltekit': 'sveltekit',
        'solid': 'solid-js',
        'qwik': 'qwik',
        'astro': 'astro',
        'eleventy': 'eleventy',
        'hugo': 'hugo',
        'jekyll': 'jekyll',
        'hexo': 'hexo',
        'gatsby': 'gatsby',
        'next': 'next',
        'nuxt': 'nuxt',
        'svelte': 'svelte',
        'sveltekit': 'sveltekit',
        'solid': 'solid-js',
        'qwik': 'qwik',
        'astro': 'astro',
        'eleventy': 'eleventy',
        'hugo': 'hugo',
        'jekyll': 'jekyll',
        'hexo': 'hexo'
    }
}


def detect_language(file_path):
    
    ext = Path(file_path).suffix.lower() # it return file path ex: m.txt it return txt

    for lang, config in LANGUAGE_PATTERNS.items():
        if ext in config['extensions']:
            return lang
    return None 

def extract_imports(file_path, language):
    """Extract non-stdlib imports from a source file."""
    try:
        
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = None
        for enc in encodings:
            # use try to catch an error
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                break # File successfully read
            except UnicodeDecodeError:
                continue 
        
        if content is None:
            print(f"⚠️  Could not decode: {file_path}")
            return set() 
        

        patterns = LANGUAGE_PATTERNS[language]['import_patterns'] #pattern
        stdlib_check = LANGUAGE_PATTERNS[language]['stdlib_check'] #Standard Library.
        imports = set()

        
        for line in content.splitlines():
            line = line.strip() #remove any space

           
            if not line or line.startswith(('#', '//')):
                continue
            
            # Check each import pattern for the language
            for pattern in patterns:

                matches = re.findall(pattern, line)

                for match in matches:
                    # import numpy.linalg
                    base = match.split('.')[0]
                    
                    # Add non-standard library imports to requirements, excluding relative imports
                    if base and not stdlib_check(base) and not base.startswith('.'):
                        imports.add(base)
                        # print(f"Found import: {base} in {file_path}")  for debugging

        return imports
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return set()

def scan_directory(path):
    path = Path(path)
    
    
    if not path.exists():
        print(f"❌ Path does not exist: {path}")
        return {}

    imports_by_language = {}

  
    files = [path] if path.is_file() else path.rglob('*')
    
    for file_path in files:
      
        if file_path.is_dir() or 'venv' in file_path.parts or '__pycache__' in file_path.parts or  'node_modules' in file_path.parts:
            continue

        
        lang = detect_language(file_path)
        if not lang:
            continue 

        
        found_imports = extract_imports(file_path, lang)
        
        # Add found imports to the dictionary
        if found_imports:
            # Use setdefault to create a set for the language if it doesn't exist
            imports_by_language.setdefault(lang, set()).update(found_imports)

    return imports_by_language

def get_latest_version(package, language):
   
    try:
        package = PACKAGE_MAP.get(language, {}).get(package, package.lower())
        
        if language == 'python':
           
            resp = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
            return resp.json()['info']['version'] if resp.status_code == 200 else None
        elif language == 'javascript':
            resp = requests.get(f"https://registry.npmjs.org/{package}/latest", timeout=5)
            return resp.json()['version'] if resp.status_code == 200 else None
    except Exception as e:
        print(f"⚠️  Failed to get version for {package}: {e}")
    return None


def generate_requirements(directory, output_file='requirements.txt'):
   
    print(f"🔍 Scanning directory: {directory}")
    all_imports = scan_directory(directory)

    
    if not all_imports:
        print("No third-party imports found.")
        return

   
    for lang, packages in all_imports.items():
        if not packages:
            continue

        print(f"\n📦 {lang.capitalize()} Packages Found ({len(packages)}):")
        
        for pkg in sorted(packages):
            print(f"  • {pkg}")

        if lang == 'python':
            with open(output_file, 'w') as f:
                for pkg in sorted(packages):
                    version = get_latest_version(pkg, lang)
                    
                    f.write(f"{pkg}=={version}\n" if version else f"{pkg}\n")
            print(f"✅ Python requirements saved to: {output_file}")

        elif lang == 'javascript':
            with open('package.json', 'w') as f:
                f.write('{\n  "dependencies": {\n')
    
                # enumerate give the index
                for i, pkg in enumerate(sorted(packages)):
                    version = get_latest_version(pkg, lang)
                    comma = ',' if i < len(packages) - 1 else ''
                    f.write(f'    "{pkg}": "{version}"{comma}\n' if version else f'    "{pkg}": "*"{comma}\n') # "*" means the latest version package.json
                f.write('  }\n}')
            print("✅ JavaScript dependencies saved to: package.json")

        else:
            # For other languages, create a generic requirements file
            file_name = f"requirements-{lang}.txt"
            with open(file_name, 'w') as f:
                for pkg in sorted(packages):
                    f.write(f"{pkg}\n")
            print(f"✅ Other language ({lang}) dependencies saved to: {file_name}")

