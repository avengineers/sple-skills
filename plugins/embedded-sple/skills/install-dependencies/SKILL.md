---
name: install-dependencies
description: Manage project dependencies using the bootstrap system. Use when users want to add, remove, or update dependencies—including Scoop packages (Windows tools) via scoopfile.json or Python packages via pyproject.toml. Triggers on requests like "add a dependency", "install tool X", "update Python package", "add scoop package", or "modify scoopfile.json/pyproject.toml".
---

# Install Dependencies

This skill covers dependency management using the bootstrap system, which automates the setup of development environments on Windows.

## Overview

The project uses [avengineers/bootstrap](https://github.com/avengineers/bootstrap) to manage dependencies:

| Dependency Type  | Configuration File | Package Manager |
|------------------|--------------------|-----------------|
| Windows tools    | `scoopfile.json`   | Scoop           |
| Python packages  | `pyproject.toml`   | Poetry/UV       |

## Running the Installer

> **BUILD**: Invoke the `build-execution` skill to install dependencies.
> Provide: install=true

Or use the VS Code task: "Install dependencies".

This executes the bootstrap process which:

1. Installs Scoop (if not present)
2. Imports packages from `scoopfile.json`
3. Installs Python (if `pyproject.toml` exists)
4. Creates virtual environment and installs Python dependencies

## Scoop Packages (scoopfile.json)

Use for installing Windows CLI tools, compilers, and system utilities.

### File Structure

```json
{
    "buckets": [
        {
            "Name": "bucket-name",
            "Source": "https://github.com/org/bucket-repo"
        }
    ],
    "apps": [
        {
            "Source": "bucket-name",
            "Name": "package-name",
            "Version": "1.2.3"
        }
    ]
}
```

The `Version` field is optional — omit it to install the latest version.

### Common Buckets

| Bucket     | Source URL                                     | Contents                         |
|------------|------------------------------------------------|----------------------------------|
| `main`     | `https://github.com/ScoopInstaller/Main`       | Core tools (git, nodejs, python) |
| `extras`   | `https://github.com/ScoopInstaller/Extras`     | GUI apps, utilities              |
| `versions` | `https://github.com/ScoopInstaller/Versions`   | Specific versions                |
| `spl`      | `https://github.com/avengineers/spl-bucket`    | SPLE-specific tools              |

### Adding a Scoop Package

1. Ensure the required bucket is listed in `buckets` array
2. Add the package to `apps` array:

```json
{
    "Source": "main",
    "Name": "nodejs"
}
```

For a specific version:

```json
{
    "Source": "versions",
    "Name": "python311",
    "Version": "3.11.9"
}
```

### Example: Add graphviz

```json
{
    "buckets": [
        {
            "Name": "main",
            "Source": "https://github.com/ScoopInstaller/Main"
        }
    ],
    "apps": [
        {
            "Source": "main",
            "Name": "nodejs"
        },
        {
            "Source": "main",
            "Name": "graphviz"
        }
    ]
}
```

## Python Packages (pyproject.toml)

Use for Python dependencies when the project needs Python tooling.

> **Why direct editing?** Edit `pyproject.toml` directly rather than using `poetry add` / `uv add`. The bootstrap system manages venv creation and dependency resolution via `build.ps1 -install` — running package manager commands outside that flow can cause lock file conflicts or bypass bootstrap's orchestration.

### File Structure

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]
```

### Adding a Python Package

Add to the `dependencies` list for runtime dependencies:

```toml
dependencies = [
    "existing-package>=1.0.0",
    "new-package>=2.0.0",
]
```

Add to `[project.optional-dependencies]` for dev/test dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "new-dev-tool>=1.0.0",
]
```

### Version Specifiers

| Specifier        | Meaning                     |
|------------------|-----------------------------|
| `>=1.0.0`        | Version 1.0.0 or higher     |
| `>=1.0.0,<2.0.0` | Between 1.0.0 and 2.0.0     |
| `~=1.0.0`        | Compatible release (~1.0.x) |
| `==1.2.3`        | Exact version               |

### Creating pyproject.toml

If the project needs Python dependencies but no `pyproject.toml` exists:

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

## Bootstrap Configuration (bootstrap.json)

Optional file to customize the bootstrap behavior:

```json
{
    "python_version": "3.11",
    "python_package_manager": "poetry>=2.1.0",
    "scoop_ignore_scoopfile": false
}
```

| Option                   | Default         | Description                    |
|--------------------------|-----------------|--------------------------------|
| `python_version`         | `3.11`          | Python version to install      |
| `python_package_manager` | `poetry>=2.1.0` | Package manager (poetry or uv) |
| `scoop_ignore_scoopfile` | `false`         | Skip scoopfile processing      |

## Workflow Summary

1. **Adding a Windows tool**: Edit `scoopfile.json` → Invoke `build-execution` with install=true
2. **Adding a Python package**: Edit `pyproject.toml` → Invoke `build-execution` with install=true
3. **Removing a Windows tool**: Delete the entry from `scoopfile.json` `apps` array (manual uninstall via `scoop uninstall <name>` if needed)
4. **Removing a Python package**: Delete the entry from `pyproject.toml` `dependencies` or `[project.optional-dependencies]` → Invoke `build-execution` with install=true

After modifying configuration files, always invoke the `build-execution` skill with install=true.

## Project Memory Integration

When adding or changing dependencies, document significant decisions using the `project-knowledge-base` skill:

- **Dependency and tool version choices (what and why)** → `doc/project_notes/decisions.md`
- **Tool versions and key configuration** → `doc/project_notes/key_facts.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure dependency decisions persist across sessions.
