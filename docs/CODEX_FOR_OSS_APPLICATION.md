# Codex for Open Source Application Prep

This document prepares honest, copy-ready material for the OpenAI Codex for Open Source application.

Official application page checked on 2026-05-31 KST:

- https://openai.com/form/codex-for-oss/

## Important Accuracy Notes

- Application is possible, but selection is not guaranteed.
- Current public GitHub adoption signals are modest: stars, forks, followers, and public issue activity are limited.
- Do not claim broad adoption, production deployment, external users, monthly downloads, or ecosystem-wide usage unless there is current evidence.
- Do not store OpenAI Organization ID, API keys, account credentials, or private email verification data in this repository.

## Recommended Repository

| Field | Value |
|---|---|
| GitHub username | `FutureAria` |
| Repository URL | `https://github.com/FutureAria/local-ai-server` |
| Recommended role | Primary maintainer |
| Project category | Local-first developer tooling, AI/RAG backend, privacy-preserving local assistant infrastructure |
| Strongest evidence | Active public maintenance, detailed README, safety policy, local CI, tests, release checklist, API/CLI contract docs |
| Weakest evidence | Low public stars/forks and limited external adoption signals |

## Why This Repository Is The Best Candidate

`local-ai-server` is the best application candidate because it is an actual developer tool with a clear open-source maintenance surface:

- FastAPI backend for local AI and document RAG workflows.
- Ollama-only runtime model and embedding calls.
- SQLite source of truth for metadata, chunks, logs, and feedback.
- Chroma local vector search.
- Typer CLI that reuses the HTTP API contract.
- Safety-first boundaries around shell, browser, file automation, cloud resources, and external LLM APIs.

## Application Form Draft

### GitHub username

```text
FutureAria
```

### GitHub repository URL

```text
https://github.com/FutureAria/local-ai-server
```

### Describe your role: are you a primary or core maintainer?

```text
Primary maintainer. I designed, implemented, documented, and maintain the repository, including the FastAPI backend, Typer CLI, local RAG workflow, safety boundaries, public release checks, and test/documentation contracts.
```

### Why does this repository qualify?

Use this 500-character-safe draft:

```text
local-ai-server is an actively maintained local-first AI knowledge server for developers and students. It provides FastAPI APIs, a Typer CLI, SQLite metadata, Chroma vector search, Ollama-only local chat/embeddings, document RAG, safety docs, release checks, and tests that guard API/README/security drift. It helps users build private local AI workflows without sending documents to external LLM APIs by default.
```

### I'm interested in

Recommended:

```text
API credits for my project
Codex Security
```

### How will you use API credits for your project?

Use this 500-character-safe draft:

```text
I would use Codex/API credits for open-source maintenance work: reviewing pull requests, improving tests, checking README/API/security documentation consistency, triaging issues, drafting release notes, and automating safe maintainer workflows. The project runtime will remain local-first by default and will not require external LLM APIs for document RAG.
```

### Anything else we should know?

Use this 500-character-safe draft:

```text
I am a student developer maintaining this as a learning and portfolio-grade OSS backend project focused on privacy, local AI, and clear safety boundaries. I understand the repository has modest adoption today, so I am applying based on active maintenance, public documentation, and the project’s usefulness for developers who want local-only AI/RAG workflows.
```

## GitHub Profile And Repository Checklist

Do these before submitting:

- [ ] Set GitHub profile name and short bio.
- [ ] Make sure profile visibility is public.
- [ ] Set repository visibility to public.
- [x] Add repository description:

```text
Local-first AI knowledge server with FastAPI, Ollama, SQLite, Chroma, RAG, and Typer CLI workflows.
```

- [x] Add repository topics:

```text
ollama, fastapi, rag, local-ai, chroma, sqlite, typer, privacy, ai-assistant, developer-tools
```

- [ ] Confirm `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `LICENSE` are visible on GitHub.
- [ ] Confirm public release check passes before pushing.
- [ ] Do not upload `.env`, local DB files, Chroma data, uploads, logs, API keys, OpenAI Organization ID, or private documents.

## 2026-05-31 GitHub Setup Status

Completed:

- Committed and pushed application prep files to `main`.
- Set repository description through the GitHub API.
- Set repository topics through the GitHub API:
  `ai-assistant`, `chroma`, `developer-tools`, `fastapi`, `local-ai`, `ollama`, `privacy`, `rag`, `sqlite`, `typer`.

Not completed automatically:

- GitHub profile bio update returned `404` through the available Git credential, likely because the credential can push to the repository but cannot update the user profile.
- OpenAI Organization ID lookup and official form submission require the user's logged-in OpenAI account and should be completed directly by the user.

## Submit Link

Submit through the official form:

- https://openai.com/form/codex-for-oss/

## Decision Required

- OpenAI Organization ID must be copied by the user from the OpenAI platform account page during form submission.
- Actual form submission should be done by the user in the browser because it may involve account login and personal account data.
- Selection is reviewed by OpenAI on a rolling basis and cannot be guaranteed.
