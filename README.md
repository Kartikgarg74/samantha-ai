# Samantha AI

**AI personal agent that executes real actions on your computer.**

Tell your computer what to do, in plain English — via voice or text. Samantha listens, understands, and acts: opens apps, controls your browser, manages files, plays music, and more.

## What It Does

- **Voice control** — Talk to your computer using natural language (Whisper-powered)
- **Browser automation** — "Search for weather in Delhi on Chrome" (Playwright)
- **System control** — "Open VS Code", "Turn up the volume", "Create a folder called Projects"
- **Media control** — "Play music on Spotify", "Pause", "Next track"
- **LLM-powered reasoning** — Uses Gemini Flash or local Ollama for understanding complex requests
- **Memory** — Learns your patterns and suggests actions based on time of day and habits

## Quick Start

```bash
# Clone
git clone https://github.com/Kartikgarg74/samantha-ai.git
cd samantha-ai

# Setup
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (or run Ollama locally)

# Run
python main.py
```

## Architecture

```
samantha-ai/
├── main.py          # Entry point — the agent loop
├── core/            # Intent classification, memory, config, session
├── voice/           # Speech recognition (Whisper) + text-to-speech
├── actions/         # What Samantha can DO (browser, system, media, messaging)
├── ai/              # LLM provider (Gemini + Ollama fallback)
└── tests/           # Real tests
```

## LLM Support

| Provider | Setup | Notes |
|----------|-------|-------|
| **Gemini Flash** | Set `GOOGLE_API_KEY` in `.env` | Primary — fast and cheap |
| **Ollama (local)** | `ollama run llama3.2` | Fallback — offline, private |

## Requirements

- macOS (primary) — Linux/Windows support planned
- Python 3.10+
- Microphone (for voice input)
- One of: Google API key or Ollama running locally

## Roadmap

- [x] Phase 1: Voice + system control + LLM brain
- [ ] Phase 2: Playwright browser automation
- [ ] Phase 3: Web dashboard + Chrome extension
- [ ] Phase 4: Research paper collection agent (vertical)

## License

MIT
