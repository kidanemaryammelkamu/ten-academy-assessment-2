# Developer MCP Tooling Strategy — git-mcp & filesystem-mcp

Purpose: document a minimal, opinionated developer stack to ensure traceability, git hygiene, and spec-aligned file editing for Project Chimera.

## Goals
- Ensure every code or spec change is traceable to a `specs/` artifact and an explicit rationale.
- Enforce consistent commit messages, branch naming, and PR metadata.
- Provide lightweight filesystem MCP tooling for spec-guided edits and safe code generation.

## git-mcp (version control logs + hygiene)

Recommended tools and plugins:
- `git` (core) — canonical source control
- `commitizen` or `cz-cli` — enforce structured commit messages (Conventional Commits)
- `pre-commit` — run linters, formatting, and commit message checks locally
- `husky` (for JS projects) or git hooks managed via `pre-commit` — enforce client-side checks

Branching & commit conventions:
- Branch names: `feat/<spec-id>-short-desc`, `fix/<spec-id>-short-desc`, `chore/<area>` where `<spec-id>` references a `specs/` file (e.g., `specs/technical.md#TaskContract`).
- Commit messages: use Conventional Commits with an extended footer mapping to specs. Example:

  feat(worker): add presence poster

  refs: specs/openclaw.md#Availability-Message-Schema
  trace: specs/hierarchical_swarm.md#Interfaces-&-Contracts

- Require a `refs:` line in the commit footer that lists one or more `specs/` file links and section identifiers.

Pre-merge CI checks:
- Schema & contract tests that validate JSON Schema/Avro against changes in `specs/` and message contracts.
- Linting, unit tests, and a `specs/trace` validator that fails the build if commits/PRs lack `refs:` entries.

PR metadata & templates:
- PR title: `<type>(<spec-id>): short description`.
- PR body must include:
  - `Specs referenced:` list of `specs/` links (mandatory)
  - `Traceability mapping:` short bullet list mapping changes → spec lines
  - `Testing:` how the change is validated

Automated changelog & release notes:
- Use changelog generation (e.g., `standard-version`) from Conventional Commits, including `refs` footers to include spec links in release notes.

Audit & append-only logs:
- Enable CI artifact storage for commit and PR metadata; persist audit logs in PostgreSQL `PRESENCE_EVENTS` or a dedicated `CHANGE_LOG` table per the Data Strategy (see specs/technical.md).

## filesystem-mcp (spec-aligned file editing)

Purpose: provide developer utilities that guide edits to files according to `specs/`, prevent accidental outward-facing outputs, and record rationale.

Core components:
- `spec-check` CLI: lightweight tool that verifies any file edits reference at least one `specs/` entry when the file affects outward-facing behavior (e.g., publishing endpoints, content generation, external APIs).
- `mcp-editor` wrapper: wraps common editors/IDEs to open the target `specs/` side-by-side and pre-populate commit footers with `refs:` and `trace:` fields.
- `generate-stub` utility: when generating code from templates, `generate-stub` inserts a header with `specs/` references and a traceability mapping placeholder that must be completed before committing.

Example `spec-check` rules:
- If a changed file path matches `scripts/*`, `src/api/*`, or any file containing `publish`/`tweet`/`webhook`, require at least one `specs/` reference in the commit or PR.
- Validate that any new outward-facing API endpoints are described in `specs/technical.md` or `specs/openclaw.md`.

Developer workflow (recommended):
1. Identify spec(s) to satisfy (open `specs/` files). Note their links/section anchors.
2. Run `mcp-editor <file>` which opens the file and the referenced specs side-by-side and creates a `TRACE.md` draft in the branch root.
3. Make edits; fill `TRACE.md` mapping each change to the exact spec clause.
4. Run `spec-check` which verifies `TRACE.md` and commit message footers; if OK, allow commit.
5. Open PR using the PR template which imports `TRACE.md` as the `Traceability mapping` section.

Security & safety gates:
- By default, any script that posts externally must include a `JUDGE_APPROVED` flag checked at runtime; `spec-check` and CI enforce this.
- Tools must respect the Prime Directive: they should refuse code generation if `TRACE.md` or `refs` are missing.

CI Integration:
- Add a `specs/trace` CI job that:
  - Lints commits for `refs:` footers.
  - Runs `spec-check` and fails builds missing required spec references.
  - Validates JSON Schema/Avro contracts against updated message definitions.

Minimal `pre-commit` config snippet (example):

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.1
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
  - repo: local
    hooks:
      - id: spec-check
        name: spec-check
        entry: scripts/spec_check.sh
        language: script
        files: ^(src/|scripts/|services/)
```

## Traceability examples
- Commit footer example:

  refs: [specs/technical.md#JSON-API-Contract, specs/openclaw.md#Availability-Message-Schema]
  trace: Implemented task queue persistence per `TASK` table fields; added presence poster using MoltBook topic `moltbook.presence.openswarm`.

## Next steps & automation opportunities
- Implement `spec-check` and `mcp-editor` prototypes.
- Add CI `specs/trace` job and a GitHub Actions workflow that enforces `refs` in PRs.
- Create a lightweight `TRACE.md` template and include it in the PR template.

---

See `specs/` for authoritative requirements and mapping; any code generation or changes must cite those files per the Prime Directive.
