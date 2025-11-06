"""
AI Trading Evolution - Documentation Generator
Avtomatik API dokumentatsiya, User Guides, Code Documentation

Bu modul barcha kodlar, API endpoints va user guides uchun
avtomatik dokumentatsiya yaratadi.
"""

import asyncio
import logging
import inspect
import ast
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FunctionDoc:
    """Function dokumentatsiyasi"""
    name: str
    signature: str
    docstring: Optional[str]
    parameters: List[Dict[str, str]]
    return_type: Optional[str]
    examples: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassDoc:
    """Class dokumentatsiyasi"""
    name: str
    docstring: Optional[str]
    bases: List[str]
    methods: List[FunctionDoc]
    attributes: List[Dict[str, str]]
    examples: List[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
    """Module dokumentatsiyasi"""
    name: str
    filepath: str
    docstring: Optional[str]
    classes: List[ClassDoc]
    functions: List[FunctionDoc]
    imports: List[str]


@dataclass
class APIEndpoint:
    """API endpoint dokumentatsiyasi"""
    path: str
    method: str  # GET, POST, PUT, DELETE
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    response: Dict[str, Any]
    examples: List[Dict[str, Any]]
    authentication: bool = False
    rate_limit: Optional[str] = None


class CodeParser:
    """
    Python kodini parse qilish va dokumentatsiya chiqarish
    """
    
    def __init__(self):
        pass
    
    def parse_file(self, filepath: str) -> ModuleDoc:
        """Python faylni parse qilish"""
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        module_doc = ModuleDoc(
            name=Path(filepath).stem,
            filepath=filepath,
            docstring=ast.get_docstring(tree),
            classes=[],
            functions=[],
            imports=[]
        )
        
        # Parse imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_doc.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module_doc.imports.append(f"from {node.module}")
        
        # Parse classes and functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self._parse_class(node)
                module_doc.classes.append(class_doc)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_doc = self._parse_function(node)
                module_doc.functions.append(func_doc)
        
        return module_doc
    
    def _parse_class(self, node: ast.ClassDef) -> ClassDoc:
        """Class ni parse qilish"""
        class_doc = ClassDoc(
            name=node.name,
            docstring=ast.get_docstring(node),
            bases=[self._get_name(base) for base in node.bases],
            methods=[],
            attributes=[]
        )
        
        # Parse methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_doc = self._parse_function(item)
                class_doc.methods.append(method_doc)
            elif isinstance(item, ast.Assign):
                # Parse class attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_doc.attributes.append({
                            'name': target.id,
                            'type': self._infer_type(item.value)
                        })
        
        return class_doc
    
    def _parse_function(self, node: ast.FunctionDef) -> FunctionDoc:
        """Function ni parse qilish"""
        # Get parameters
        parameters = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_annotation(arg.annotation) if arg.annotation else 'Any'
            }
            parameters.append(param)
        
        # Get return type
        return_type = None
        if node.returns:
            return_type = self._get_annotation(node.returns)
        
        # Get decorators
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        
        func_doc = FunctionDoc(
            name=node.name,
            signature=self._get_function_signature(node),
            docstring=ast.get_docstring(node),
            parameters=parameters,
            return_type=return_type,
            decorators=decorators
        )
        
        return func_doc
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Function signature ni olish"""
        args_str = ', '.join(arg.arg for arg in node.args.args)
        return f"{node.name}({args_str})"
    
    def _get_annotation(self, node) -> str:
        """Type annotation ni olish"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "Any"
    
    def _get_name(self, node) -> str:
        """Node nomini olish"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return str(node)
    
    def _infer_type(self, node) -> str:
        """Type ni infer qilish"""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "List"
        elif isinstance(node, ast.Dict):
            return "Dict"
        elif isinstance(node, ast.Set):
            return "Set"
        else:
            return "Any"


class APIDocGenerator:
    """
    API Documentation Generator
    
    OpenAPI/Swagger formatida API dokumentatsiya yaratish
    """
    
    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
    
    def add_endpoint(self, endpoint: APIEndpoint):
        """Endpoint qo'shish"""
        self.endpoints.append(endpoint)
    
    def discover_endpoints(self, code: str) -> List[APIEndpoint]:
        """Koddan endpoint larni topish"""
        endpoints = []
        
        # Flask route pattern
        flask_pattern = r'@app\.route\([\'"](.+?)[\'"]\s*,?\s*methods=\[([^\]]+)\]'
        matches = re.finditer(flask_pattern, code)
        
        for match in matches:
            path = match.group(1)
            methods = match.group(2).replace("'", "").replace('"', '').split(',')
            
            for method in methods:
                endpoint = APIEndpoint(
                    path=path,
                    method=method.strip(),
                    description=f"API endpoint: {method.strip()} {path}",
                    parameters=[],
                    request_body=None,
                    response={'type': 'object'},
                    examples=[]
                )
                endpoints.append(endpoint)
        
        return endpoints
    
    def generate_openapi_spec(self, title: str = "AI Trading Evolution API",
                             version: str = "1.0.0") -> Dict[str, Any]:
        """OpenAPI 3.0 specification yaratish"""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': title,
                'version': version,
                'description': 'AI Trading Evolution API documentation'
            },
            'servers': [
                {
                    'url': 'https://api.trading.example.com',
                    'description': 'Production server'
                }
            ],
            'paths': {}
        }
        
        # Add endpoints
        for endpoint in self.endpoints:
            if endpoint.path not in spec['paths']:
                spec['paths'][endpoint.path] = {}
            
            spec['paths'][endpoint.path][endpoint.method.lower()] = {
                'summary': endpoint.description,
                'parameters': endpoint.parameters,
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': {
                            'application/json': {
                                'schema': endpoint.response
                            }
                        }
                    }
                }
            }
            
            if endpoint.request_body:
                spec['paths'][endpoint.path][endpoint.method.lower()]['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': endpoint.request_body
                        }
                    }
                }
            
            if endpoint.authentication:
                spec['paths'][endpoint.path][endpoint.method.lower()]['security'] = [
                    {'bearerAuth': []}
                ]
        
        # Add security schemes
        spec['components'] = {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }
        
        return spec


class MarkdownGenerator:
    """
    Markdown dokumentatsiya generator
    """
    
    def __init__(self):
        pass
    
    def generate_module_docs(self, module_doc: ModuleDoc) -> str:
        """Module uchun markdown dokumentatsiya"""
        md = f"# {module_doc.name}\n\n"
        
        if module_doc.docstring:
            md += f"{module_doc.docstring}\n\n"
        
        # Table of contents
        md += "## Mundarija\n\n"
        if module_doc.classes:
            md += "### Klasslar\n"
            for cls in module_doc.classes:
                md += f"- [{cls.name}](#{cls.name.lower()})\n"
            md += "\n"
        
        if module_doc.functions:
            md += "### Funksiyalar\n"
            for func in module_doc.functions:
                md += f"- [{func.name}](#{func.name.lower()})\n"
            md += "\n"
        
        # Classes
        if module_doc.classes:
            md += "## Klasslar\n\n"
            for cls in module_doc.classes:
                md += self._generate_class_doc(cls)
        
        # Functions
        if module_doc.functions:
            md += "## Funksiyalar\n\n"
            for func in module_doc.functions:
                md += self._generate_function_doc(func)
        
        return md
    
    def _generate_class_doc(self, class_doc: ClassDoc) -> str:
        """Class dokumentatsiyasi"""
        md = f"### {class_doc.name}\n\n"
        
        if class_doc.bases:
            md += f"**Inheritance:** {', '.join(class_doc.bases)}\n\n"
        
        if class_doc.docstring:
            md += f"{class_doc.docstring}\n\n"
        
        # Attributes
        if class_doc.attributes:
            md += "**Atributlar:**\n\n"
            for attr in class_doc.attributes:
                md += f"- `{attr['name']}` ({attr['type']})\n"
            md += "\n"
        
        # Methods
        if class_doc.methods:
            md += "**Metodlar:**\n\n"
            for method in class_doc.methods:
                md += self._generate_function_doc(method, is_method=True)
        
        return md
    
    def _generate_function_doc(self, func_doc: FunctionDoc, is_method: bool = False) -> str:
        """Function/method dokumentatsiyasi"""
        prefix = "####" if is_method else "###"
        md = f"{prefix} {func_doc.name}\n\n"
        
        # Signature
        md += f"```python\n{func_doc.signature}\n```\n\n"
        
        # Decorators
        if func_doc.decorators:
            md += f"**Dekoratorlar:** {', '.join(func_doc.decorators)}\n\n"
        
        # Docstring
        if func_doc.docstring:
            md += f"{func_doc.docstring}\n\n"
        
        # Parameters
        if func_doc.parameters:
            md += "**Parametrlar:**\n\n"
            for param in func_doc.parameters:
                md += f"- `{param['name']}` ({param['type']})\n"
            md += "\n"
        
        # Return type
        if func_doc.return_type:
            md += f"**Qaytaradi:** `{func_doc.return_type}`\n\n"
        
        # Examples
        if func_doc.examples:
            md += "**Misollar:**\n\n"
            for example in func_doc.examples:
                md += f"```python\n{example}\n```\n\n"
        
        return md
    
    def generate_api_docs(self, endpoints: List[APIEndpoint]) -> str:
        """API endpoints uchun markdown dokumentatsiya"""
        md = "# API Documentation\n\n"
        
        # Group by path
        grouped = {}
        for endpoint in endpoints:
            if endpoint.path not in grouped:
                grouped[endpoint.path] = []
            grouped[endpoint.path].append(endpoint)
        
        # Generate docs for each path
        for path, path_endpoints in grouped.items():
            md += f"## {path}\n\n"
            
            for endpoint in path_endpoints:
                md += f"### {endpoint.method}\n\n"
                md += f"{endpoint.description}\n\n"
                
                if endpoint.authentication:
                    md += "🔒 **Autentifikatsiya talab qilinadi**\n\n"
                
                if endpoint.parameters:
                    md += "**Parametrlar:**\n\n"
                    md += "| Nom | Turi | Tavsif |\n"
                    md += "|-----|------|--------|\n"
                    for param in endpoint.parameters:
                        md += f"| {param.get('name', '-')} | {param.get('type', '-')} | {param.get('description', '-')} |\n"
                    md += "\n"
                
                if endpoint.request_body:
                    md += "**Request Body:**\n\n"
                    md += f"```json\n{json.dumps(endpoint.request_body, indent=2)}\n```\n\n"
                
                md += "**Response:**\n\n"
                md += f"```json\n{json.dumps(endpoint.response, indent=2)}\n```\n\n"
                
                if endpoint.examples:
                    md += "**Misollar:**\n\n"
                    for example in endpoint.examples:
                        md += f"```bash\n{example.get('curl', '')}\n```\n\n"
        
        return md


class DocumentationGenerator:
    """
    Comprehensive Documentation Generator
    
    Barcha dokumentatsiya turlarini yaratish
    """
    
    def __init__(self, project_root: str = '/workspace/code',
                 output_dir: str = '/workspace/docs'):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.code_parser = CodeParser()
        self.api_doc_generator = APIDocGenerator()
        self.markdown_generator = MarkdownGenerator()
    
    async def generate_all_docs(self):
        """Barcha dokumentatsiyalarni yaratish"""
        logger.info("=" * 80)
        logger.info("Generating Comprehensive Documentation")
        logger.info("=" * 80)
        
        # 1. Code documentation
        logger.info("\n[1/4] Generating Code Documentation")
        logger.info("-" * 80)
        await self._generate_code_docs()
        
        # 2. API documentation
        logger.info("\n[2/4] Generating API Documentation")
        logger.info("-" * 80)
        await self._generate_api_docs()
        
        # 3. User guide
        logger.info("\n[3/4] Generating User Guide")
        logger.info("-" * 80)
        await self._generate_user_guide()
        
        # 4. README
        logger.info("\n[4/4] Generating README")
        logger.info("-" * 80)
        await self._generate_readme()
        
        logger.info("\n✓ Dokumentatsiya yaratildi!")
        logger.info(f"Joylashuv: {self.output_dir}")
    
    async def _generate_code_docs(self):
        """Kod dokumentatsiyasini yaratish"""
        python_files = list(self.project_root.rglob('*.py'))
        
        logger.info(f"Parsing {len(python_files)} Python files...")
        
        docs_by_category = {
            'strategies': [],
            'analytics': [],
            'markets': [],
            'ml': [],
            'integration': []
        }
        
        for filepath in python_files:
            try:
                module_doc = self.code_parser.parse_file(str(filepath))
                
                # Categorize
                relative_path = filepath.relative_to(self.project_root)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'other'
                
                if category in docs_by_category:
                    docs_by_category[category].append(module_doc)
                
                # Generate markdown
                md_content = self.markdown_generator.generate_module_docs(module_doc)
                
                # Save to file
                output_file = self.output_dir / f"code_{module_doc.name}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                logger.info(f"✓ Generated docs for {module_doc.name}")
                
            except Exception as e:
                logger.error(f"Failed to parse {filepath}: {e}")
        
        # Generate index
        await self._generate_code_index(docs_by_category)
    
    async def _generate_code_index(self, docs_by_category: Dict[str, List[ModuleDoc]]):
        """Kod dokumentatsiyasi indeksini yaratish"""
        md = "# Kod Dokumentatsiyasi\n\n"
        md += "Barcha modullar va ularning dokumentatsiyasi.\n\n"
        
        for category, modules in docs_by_category.items():
            if modules:
                md += f"## {category.title()}\n\n"
                for module in modules:
                    md += f"- [{module.name}](code_{module.name}.md)\n"
                md += "\n"
        
        index_file = self.output_dir / "code_index.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info("✓ Generated code documentation index")
    
    async def _generate_api_docs(self):
        """API dokumentatsiyasini yaratish"""
        # Discover API endpoints from code
        # In real scenario, would scan all API files
        
        # Generate OpenAPI spec
        openapi_spec = self.api_doc_generator.generate_openapi_spec()
        
        # Save OpenAPI spec
        openapi_file = self.output_dir / "openapi.json"
        with open(openapi_file, 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        
        # Generate markdown
        md_content = self.markdown_generator.generate_api_docs(self.api_doc_generator.endpoints)
        
        api_docs_file = self.output_dir / "api_documentation.md"
        with open(api_docs_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info("✓ Generated API documentation")
    
    async def _generate_user_guide(self):
        """Foydalanuvchi qo'llanmasini yaratish"""
        md = """# AI Trading Evolution - Foydalanuvchi Qo'llanmasi

## Kirish

AI Trading Evolution - bu sun'iy intellekt va mashinani o'rganish asosida ishlaydigan
professional trading platformasi.

## O'rnatish

### Talablar

- Python 3.9+
- PostgreSQL 14+
- Redis 6+

### Qadamlar

1. Repository ni klonlang:
```bash
git clone https://github.com/your-org/ai-trading-evolution.git
cd ai-trading-evolution
```

2. Virtual environment yarating:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```

3. Dependencies ni o'rnating:
```bash
pip install -r requirements.txt
```

4. Environment variables ni sozlang:
```bash
cp .env.example .env
# .env faylni tahrirlang
```

5. Database ni migrate qiling:
```bash
python manage.py migrate
```

6. Ilovani ishga tushiring:
```bash
python manage.py runserver
```

## Asosiy Funksiyalar

### 1. Trading Strategiyalari

#### Arbitrage Trading
CEX va DEX orasidagi narx farqlarini topib, foyda olish.

#### Grid Trading
Narx oralig'ida avtomatik buy/sell orderlar berish.

#### DCA (Dollar Cost Averaging)
Ma'lum vaqt oralig'ida muntazam xarid qilish.

### 2. Analytics va Monitoring

#### Sentiment Analysis
Twitter, Reddit va boshqa manbalardan sentiment tahlili.

#### Whale Tracking
Yirik tranzaksiyalarni real-time kuzatish.

#### Risk Scoring
Portfolio xavfini baholash va tavsialar.

### 3. ML Models

#### Reinforcement Learning
SAC, TD3, Rainbow DQN algoritmlari bilan trading.

#### Predictive Models
LSTM, Transformer va Hybrid modellar bilan narx bashorati.

#### Emotion AI
Bozor psixologiyasi va Fear & Greed Index.

## Tez-tez So'raladigan Savollar (FAQ)

### Platformani qanday ishga tushiraman?
`python manage.py runserver` buyrug'i bilan.

### Qanday exchange'lar qo'llab-quvvatlanadi?
Binance, Coinbase, Kraken, va boshqalar.

### Minimal investitsiya miqdori?
$100 dan boshlanadi.

### API key'larni qayerda sozlayman?
Admin panelda Settings > API Configuration bo'limida.

## Texnik Qo'llab-quvvatlash

Savollar uchun:
- Email: support@trading.example.com
- Telegram: @trading_support
- Discord: discord.gg/trading
"""
        
        user_guide_file = self.output_dir / "user_guide.md"
        with open(user_guide_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info("✓ Generated user guide")
    
    async def _generate_readme(self):
        """README ni yaratish"""
        md = """# AI Trading Evolution

🚀 Professional AI-powered trading platform

## Features

- ✅ 6 Advanced Trading Strategies
- ✅ 6 Analytics & Monitoring Tools
- ✅ Multi-market Support (Crypto, Stocks, Commodities, Bonds, ETFs)
- ✅ 6 ML/AI Models (RL, Predictive, Emotion AI)
- ✅ Full-stack Admin Panel
- ✅ Comprehensive Testing Framework
- ✅ Performance Optimization
- ✅ Security Auditing

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/ai-trading-evolution.git

# Install dependencies
pip install -r requirements.txt

# Run application
python manage.py runserver
```

## Documentation

- [User Guide](docs/user_guide.md)
- [API Documentation](docs/api_documentation.md)
- [Code Documentation](docs/code_index.md)

## Architecture

```
├── strategies/       # Trading strategies
├── analytics/        # Analytics & monitoring
├── markets/          # Market integrations
├── ml/              # ML/AI models
└── integration/     # Integration & deployment
```

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL
- **Frontend:** React, TypeScript, Tailwind CSS
- **ML:** PyTorch, TensorFlow
- **Deployment:** Docker, Kubernetes

## License

MIT License

## Support

- Email: support@trading.example.com
- Telegram: @trading_support
"""
        
        readme_file = self.output_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info("✓ Generated README")


# Example usage
async def main():
    """Documentation generator demo"""
    doc_generator = DocumentationGenerator()
    
    # Generate all documentation
    await doc_generator.generate_all_docs()


if __name__ == '__main__':
    asyncio.run(main())
