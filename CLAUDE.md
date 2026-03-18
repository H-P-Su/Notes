# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

**Notes** is a personal notes repository. It is intentionally minimal — a plain text/markdown collection with no build system, dependencies, or source code.

- **Owner**: Hua Su
- **Remote**: `http://local_proxy@127.0.0.1:43089/git/H-P-Su/Notes`
- **Default branch**: `master`

## Repository Structure

```
Notes/
├── README.md       # Minimal project description
└── CLAUDE.md       # This file
```

## Development Conventions

### Branching

- Feature branches follow the pattern: `claude/<description>-<id>`
- Push to the designated feature branch; never push directly to `master` without explicit permission.

### Commits

- Write clear, descriptive commit messages that explain *what* and *why*.
- Keep commits focused and atomic.

### File Format

- Use Markdown (`.md`) for all notes and documentation.
- Keep formatting simple and readable.

## Working with This Repository

Since there is no build system or test suite, the primary tasks in this repo are:

1. **Adding notes** — create or edit `.md` files.
2. **Organizing content** — structure notes into directories as the collection grows.
3. **Documentation** — keep `README.md` and `CLAUDE.md` up to date as the repo evolves.

## Git Workflow

```bash
# Push changes to a feature branch
git push -u origin <branch-name>

# Fetch a specific branch
git fetch origin <branch-name>
```

Always use `git push -u origin <branch-name>` (not bare `git push`) to ensure tracking is set correctly.

## Notes for AI Assistants

- This repo has no linter, formatter, or test runner — skip any steps that assume these exist.
- Do not add unnecessary configuration files, build tooling, or dependencies unless explicitly requested.
- When adding notes, prefer plain Markdown without complex front matter unless the user requests it.
- Keep changes minimal and focused on what was asked.
