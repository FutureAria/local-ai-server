# Contributing

Thank you for considering a contribution to `local-ai-server`.

This project is a local-first AI knowledge server for developers and students who want document search, RAG, and assistant-style workflows without sending private documents to external LLM APIs by default.

## Project Boundaries

Before opening an issue or pull request, please keep these boundaries in mind:

- Runtime LLM and embedding calls use Ollama local API only.
- OpenAI, Claude, Gemini, hosted embeddings, and cloud vector DBs are not part of the default runtime.
- The default server bind example is `127.0.0.1`.
- Browser interaction, shell execution, file modification automation, cloud deployment, and Oracle resource changes are out of scope unless a separate security review and maintainer approval happen first.
- Do not include secrets, API keys, tokens, database passwords, Oracle wallets, private documents, local databases, Chroma indexes, uploads, or logs in issues or pull requests.

## Good First Contributions

Helpful contributions include:

- Documentation fixes and clearer examples.
- Tests that prevent API, CLI, README, and security-policy drift.
- Safer error messages and validation.
- Local-only workflow improvements for FastAPI, Typer, SQLite, Chroma, and Ollama.
- UI integration examples that consume the existing API contract without changing the backend safety boundary.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,documents]"
```

Ollama is only required for runtime RAG or smoke tests that call local models. Static tests and import checks should work without Ollama running.

## Verification

Run the local CI script before opening a pull request:

```bash
.venv/bin/python scripts/local_ci_check.py --root .
```

The script runs:

1. `.venv/bin/python -m pytest`
2. `.venv/bin/python -m compileall app cli scripts`
3. `.venv/bin/python scripts/public_release_check.py --root . --json`
4. `git diff --check`

## Pull Request Checklist

- [ ] The change stays inside the local-first project boundary.
- [ ] No secrets, private documents, local DB files, Chroma indexes, uploads, or logs are included.
- [ ] README, API docs, SECURITY.md, and tests are updated when contracts change.
- [ ] `scripts/local_ci_check.py --root .` was run, or the reason it could not be run is written in the PR.
- [ ] Any security, cloud, external API, browser interaction, shell execution, or file automation change is clearly marked for maintainer review before implementation.

