# Gemini CLI + Docker Compose (Minimal, fast)

Run the official **Gemini CLI** inside a reproducible container. Works on macOS/Windows/Linux and Apple Silicon.

## Quick start

```bash
# 1) Unzip and cd into this folder
# 2) Copy env template and add your key
cp .env.example .env
#   - For AI Studio: put your GEMINI_API_KEY
#   - For Vertex AI: set GOOGLE_API_KEY and set GOOGLE_GENAI_USE_VERTEXAI=true

# 3) Start an interactive shell that has `gemini` installed
docker compose -f docker-compose-gemini.yml run --rm -it gemini

# 4) Inside the container, talk to Gemini
gemini /help
gemini -p "このリポジトリの設計を要約して"
gemini -m gemini-2.5-pro -p "README を改善して Pull Request 文面も書いて"
```

> Tip: your host directory is mounted to `/workspace`, so `/workspace` == your project root.

## Project-aware usage

From inside the shell:

```bash
# Start a session with current project context
gemini

# Include specific directories
gemini --include-directories src,docs

# One-shot prompt (non-interactive)
gemini -p "tests のカバレッジを上げるための TODO を 5 個"
```

## Auth Options

- **AI Studio API key (simple)**: set `GEMINI_API_KEY`.
- **Vertex AI**: set `GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI=true`, and optionally `GOOGLE_CLOUD_PROJECT` for org quotas.

See the upstream docs for quotas, models, and auth flows.

## Extras

Project-level settings live in `./.gemini/`:
- `settings.json` – default model, telemetry, etc.
- `GEMINI.md` – long-lived context & writing style for this repo.

## Remove

```bash
docker compose down --rmi local -v
```

---

**References**
- Gemini CLI overview & quotas (Google Cloud docs)  
- Install & auth options (GitHub README)