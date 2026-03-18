# uv — Python Package Manager

## Installation
```bash
curl -Lsf https://astral.sh/uv/install.sh | sh
```

## Projects

| Command | Action |
|---------|--------|
| `uv init my-project` | Create a new project |
| `uv init --lib` | Create a library project |
| `uv run script.py` | Run a script in the project environment |

## Python Versions

| Command | Action |
|---------|--------|
| `uv python install 3.12` | Install a Python version |
| `uv python list` | List available/installed versions |
| `uv python pin 3.12` | Pin project to a Python version |

## Dependencies

| Command | Action |
|---------|--------|
| `uv add requests` | Add a dependency |
| `uv add --dev pytest` | Add a dev dependency |
| `uv remove requests` | Remove a dependency |
| `uv sync` | Install all dependencies from lockfile |
| `uv lock` | Update the lockfile without installing |
| `uv tree` | Show dependency tree |

## Virtual Environments

| Command | Action |
|---------|--------|
| `uv venv` | Create a `.venv` in current directory |
| `uv venv --python 3.12` | Create venv with specific Python |
| `source .venv/bin/activate` | Activate (Linux/macOS) |
| `.venv\Scripts\activate` | Activate (Windows) |

## Packages (pip replacement)

| Command | Action |
|---------|--------|
| `uv pip install requests` | Install a package |
| `uv pip install -r requirements.txt` | Install from requirements file |
| `uv pip uninstall requests` | Uninstall a package |
| `uv pip list` | List installed packages |
| `uv pip freeze` | Output installed packages as requirements |
| `uv pip compile requirements.in` | Compile pinned requirements |

## Tools (pipx replacement)

| Command | Action |
|---------|--------|
| `uv tool install ruff` | Install a CLI tool globally |
| `uv tool run ruff check .` | Run a tool without installing |
| `uvx ruff check .` | Shorthand for `uv tool run` |
| `uv tool list` | List installed tools |
| `uv tool uninstall ruff` | Uninstall a tool |
