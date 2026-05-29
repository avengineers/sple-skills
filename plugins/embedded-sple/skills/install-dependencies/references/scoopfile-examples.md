# Scoop Configuration Examples

## Complete scoopfile.json Examples

### Minimal (Node.js project)

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
        }
    ]
}
```

### With Build Tools

```json
{
    "buckets": [
        {
            "Name": "main",
            "Source": "https://github.com/ScoopInstaller/Main"
        },
        {
            "Name": "extras",
            "Source": "https://github.com/ScoopInstaller/Extras"
        }
    ],
    "apps": [
        {
            "Source": "main",
            "Name": "nodejs"
        },
        {
            "Source": "main",
            "Name": "make"
        },
        {
            "Source": "main",
            "Name": "cmake"
        }
    ]
}
```

### With Specific Versions

```json
{
    "buckets": [
        {
            "Name": "main",
            "Source": "https://github.com/ScoopInstaller/Main"
        },
        {
            "Name": "versions",
            "Source": "https://github.com/ScoopInstaller/Versions"
        }
    ],
    "apps": [
        {
            "Source": "versions",
            "Name": "nodejs18",
            "Version": "18.20.0"
        },
        {
            "Source": "versions",
            "Name": "python311"
        }
    ]
}
```

### SPLE Project with Custom Bucket

```json
{
    "buckets": [
        {
            "Name": "main",
            "Source": "https://github.com/ScoopInstaller/Main"
        },
        {
            "Name": "spl",
            "Source": "https://github.com/avengineers/spl-bucket"
        }
    ],
    "apps": [
        {
            "Source": "main",
            "Name": "nodejs"
        },
        {
            "Source": "spl",
            "Name": "mingw-winlibs-llvm-ucrt",
            "Version": "13.2.0-16.0.6-11.0.0-r1"
        }
    ]
}
```

## Common Scoop Packages

### Development Tools

| Package | Bucket | Description |
|---------|--------|-------------|
| `git` | main | Version control |
| `nodejs` | main | Node.js runtime (LTS) |
| `nodejs18` | versions | Node.js 18.x |
| `python` | main | Python (latest) |
| `python311` | versions | Python 3.11.x |
| `vscode` | extras | Visual Studio Code |

### Build Tools

| Package | Bucket | Description |
|---------|--------|-------------|
| `make` | main | GNU Make |
| `cmake` | main | CMake build system |
| `ninja` | main | Ninja build system |
| `gcc` | main | GCC compiler |
| `llvm` | main | LLVM/Clang |

### Utilities

| Package | Bucket | Description |
|---------|--------|-------------|
| `jq` | main | JSON processor |
| `yq` | main | YAML processor |
| `graphviz` | main | Graph visualization |
| `pandoc` | main | Document converter |
| `plantuml` | extras | UML diagrams |

## Bucket URLs Reference

| Bucket | URL |
|--------|-----|
| main | `https://github.com/ScoopInstaller/Main` |
| extras | `https://github.com/ScoopInstaller/Extras` |
| versions | `https://github.com/ScoopInstaller/Versions` |
| java | `https://github.com/ScoopInstaller/Java` |
| nerd-fonts | `https://github.com/matthewjberger/scoop-nerd-fonts` |
| spl | `https://github.com/avengineers/spl-bucket` |

## Troubleshooting

### Package not found

1. Verify bucket is added to `buckets` array
2. Check package name at [scoop.sh](https://scoop.sh/) or bucket repo
3. Use `scoop search <name>` to find correct name

### Version conflicts

If a tool is already installed with a different version:

```powershell
# Reset shims after install
scoop reset <package>
```

### Scoop not installing

Ensure PowerShell execution policy allows scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -install
```
