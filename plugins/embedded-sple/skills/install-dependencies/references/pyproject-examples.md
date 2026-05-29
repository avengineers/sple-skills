# Python Project Configuration Examples

## Complete pyproject.toml Examples

### Minimal Application

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### With Runtime Dependencies

```toml
[project]
name = "my-project"
version = "1.0.0"
description = "A Python application"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
    "click>=8.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### With Dev Dependencies

```toml
[project]
name = "my-project"
version = "1.0.0"
description = "A Python application"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### Complete Package with Entry Points

```toml
[project]
name = "my-cli-tool"
version = "1.0.0"
description = "A CLI tool"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Author Name", email = "author@example.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
my-tool = "my_package.cli:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### Using Poetry Backend

```toml
[tool.poetry]
name = "my-project"
version = "1.0.0"
description = "A Python application"
authors = ["Author <author@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.28.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
ruff = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Version Specifier Reference

| Specifier | Meaning | Example |
|-----------|---------|---------|
| `>=X.Y.Z` | Minimum version | `requests>=2.28.0` |
| `>=X.Y.Z,<A.B.C` | Version range | `pydantic>=2.0.0,<3.0.0` |
| `~=X.Y.Z` | Compatible release | `click~=8.0.0` (any 8.0.x) |
| `==X.Y.Z` | Exact version | `numpy==1.24.3` |
| `!=X.Y.Z` | Exclude version | `setuptools!=50.0.0` |
| `^X.Y.Z` | (Poetry) Compatible | `^2.28.0` (>=2.28.0,<3.0.0) |

## Common Python Packages

### Web/HTTP

| Package | Description |
|---------|-------------|
| `requests` | HTTP library |
| `httpx` | Async HTTP client |
| `aiohttp` | Async HTTP |
| `flask` | Web framework |
| `fastapi` | Modern API framework |

### CLI

| Package | Description |
|---------|-------------|
| `click` | CLI framework |
| `typer` | Modern CLI (click-based) |
| `rich` | Terminal formatting |
| `argparse` | (stdlib) Argument parsing |

### Data

| Package | Description |
|---------|-------------|
| `pydantic` | Data validation |
| `pandas` | Data analysis |
| `numpy` | Numerical computing |
| `polars` | Fast DataFrames |

### Testing/Dev

| Package | Description |
|---------|-------------|
| `pytest` | Test framework |
| `pytest-cov` | Coverage plugin |
| `ruff` | Fast linter/formatter |
| `mypy` | Type checker |
| `black` | Code formatter |

## Bootstrap Configuration

### bootstrap.json for Python Projects

```json
{
    "python_version": "3.11",
    "python_package_manager": "poetry>=2.1.0"
}
```

### Using UV Package Manager

```json
{
    "python_version": "3.12",
    "python_package_manager": "uv>=0.1.0"
}
```

## Virtual Environment

After running `.\build.ps1 -install`, the virtual environment is created at `.venv/`.

### Activate Manually

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# Command Prompt
.\.venv\Scripts\activate.bat
```

### VS Code Integration

VS Code automatically detects `.venv` and offers to use it as the Python interpreter.

## Troubleshooting

### Package installation fails

1. Check internet connectivity
2. Verify package name spelling
3. Check version compatibility with Python version

### Virtual environment issues

1. Close VS Code (it may hold handles on Python)
2. Delete `.venv` folder
3. Run `.\build.ps1 -install` again

### Poetry lock conflicts

```powershell
# Delete lock and reinstall
Remove-Item poetry.lock
.\build.ps1 -install
```
