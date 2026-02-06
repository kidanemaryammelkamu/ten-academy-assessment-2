<!-- Repository Copilot / assistant guidance -->
# Copilot Instructions

This file contains concise guidance for AI-assisted edits, code style, and expectations when contributing to this repository.

Principles
- Keep changes minimal and focused to the task.
- Prefer clarity over cleverness; maintain readability.
- Preserve existing project structure and public APIs unless a breaking change is explicitly requested.

Coding style
- Follow the project's Python conventions (type hints, descriptive names, no one-letter vars).
- Add small, focused functions. Favor composition over long functions.
- Use the existing formatting and linting tools (respect `pyproject.toml`).

Tests & verification
- When adding or changing logic, include a small unit test where practical.
- Run existing test suites locally before suggesting merges.

Security & secrets
- Never add secrets, tokens, credentials, or private keys to the repo.
- If a secret is needed, instruct the user to use environment variables or a secrets manager.

Commits & PRs
- Keep commits atomic and message them clearly (what + why).
- For suggested PRs, include a short summary, testing steps, and any migration notes.

Database & migrations
- Prefer explicit SQL migrations (or Alembic) for schema changes. Include rollback notes.

If uncertain
- Ask for clarification instead of guessing large design changes.

Contact
- If you need the original file restored differently, request changes and provide any missing content you remember.
