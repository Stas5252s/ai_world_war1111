# AI WORLD WAR — MVP 0.1

A one-evening prototype of an autonomous geopolitical strategy sandbox. Ten country agents choose one action per turn. A deterministic engine resolves GDP, stability, technology, population, resources, relations and abstract strategic contests.

**Fictional game simulation:** initial country attributes are synthetic balance values, not current real-world statistics. Conflict is abstract and non-operational.

## Run on macOS

```bash
cd ai_world_war
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Local AI with Ollama

```bash
ollama pull qwen2.5:3b
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:3b
```

Choose **Ollama** for countries in the AI agents tab. Ten local calls per turn can take a while on a 16 GB laptop. Start with one or two Ollama agents and leave the rest on Fallback.

## Cloud API

Before launching Streamlit:

```bash
export CLOUD_BASE_URL=https://api.openai.com/v1
export CLOUD_API_KEY="your_key"
export CLOUD_MODEL="gpt-4.1-mini"
```

The endpoint must support an OpenAI-compatible `/chat/completions` API and JSON response mode. Never commit API keys.

## Structure

- `app.py` — Streamlit dashboard, map, metrics, event log and player controls.
- `worldwar/data.py` — synthetic country profiles and action catalogue.
- `worldwar/agents.py` — Ollama, cloud and deterministic fallback decision providers.
- `worldwar/engine.py` — world state, turn resolution and interventions.

## MVP mechanics

Each turn, all ten agents receive the same pre-resolution snapshot and choose one action. The engine then resolves decisions and background changes. Player interventions are applied immediately. Campaign persistence, treaties, elections, private intelligence and continuous simulation are planned upgrades.
