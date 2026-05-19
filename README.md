# Building Agentic AI Systems — Tutorial

A 1-hour hands-on introduction to agentic AI for bioinformaticians. Built around a single running example: an agent that extracts structured information from PubMed-style abstracts.

## Online

Lab: https://colab.research.google.com/github/fifteen02/agentic-tutorial/blob/main/NB01_tutorial.ipynb

Solutions: https://colab.research.google.com/github/fifteen02/agentic-tutorial/blob/main/NB01_tutorial_solutions.ipynb

Agentomics Tutorial: https://colab.research.google.com/github/fifteen02/agentic-tutorial/blob/main/agentomics_workshop.ipynb

## What's in this folder

| File | What it is |
|---|---|
| `NB01_tutorial.ipynb` | The student tutorial notebook — six core sections (§1–§6) plus five bonus sections (§7–§11). Has `# TODO` markers for hands-on exercises. |
| `NB01_tutorial_solutions.ipynb` | Same notebook with all TODOs filled in. |
| `requirements.txt` | Python dependencies. |
| `abstracts.json` | Created automatically when the notebook runs — five cached PubMed-style abstracts used throughout the tutorial. |

## Tutorial outline

A single agent grows across the notebook. Each section adds one capability:

| § | Topic | What you build |
|---|---|---|
| 1 | Chat vs Agent | First agent — `get_today()` tool fixes a date-question failure |
| 2 | The agent loop | Inspect `result.all_messages()` to see the 5-step tool-call cycle |
| 3 | Tools | `pubmed_search` + `run_python` — sandboxed code execution |
| 4 | Structured results | Pydantic `PaperSummary` schema with regex-validated PMID |
| 5 | Context | Conversation history, document-in-prompt, mini-RAG with sentence-transformers |
| 6 | Multi-agent | Orchestrator-worker: extractor + summariser + driver function |
| **Bonus (covered if time permits):** | | |
| 7 | Real MCP in the wild | Five recipes: BioMCP (pip), Fetch (uvx), Filesystem (npx), GitHub (auth), UniProt (clone+build) |
| 8 | Reflection | Critic agent + extract→critique→re-extract loop |
| 9 | Reasoning models | Switch `MODEL_SLUG` to a reasoning model and compare outputs |
| 10 | Evals | Code-based, shared-rule, and LLM-as-judge eval patterns |
| 11 | Memory | File-based persistent memory across "sessions" |

The full conceptual companion is in `module_guide.pdf` — it's the reference document the notebook is built against.

## Local setup

Requires Python 3.11+ and an OpenRouter API key (free tier at https://openrouter.ai).

### One-time setup

```bash
cd path/to/this/tutorial

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Install dependencies (~2–3 min on first install — pulls torch via sentence-transformers)
pip install -r requirements.txt
```

Or with `uv` (≈10× faster):

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Optional extras for the §7 MCP recipes

| Recipe | Extra prerequisite |
|---|---|
| Fetch (recipe 2) | `uv` — `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Filesystem (recipe 3) | Node.js — `brew install node` or download from nodejs.org |
| GitHub (recipe 4) | A GitHub personal access token with `repo` scope, exported as `GITHUB_TOKEN` |
| UniProt (recipe 5) | Manual clone + `npm install && npm run build` of the UniProt MCP repo |

## Running the notebook

### In Cursor / VS Code

1. Open this folder in Cursor.
2. Open `NB01_tutorial.ipynb`.
3. Top-right corner → **Select Kernel** → **Python Environments…** → pick the one ending `.venv`.
4. Run cells with `Shift+Enter`, or **Run All** from the toolbar.

If the venv doesn't appear in the kernel picker:
- `Cmd+Shift+P` → `Python: Select Interpreter` → **Enter interpreter path…** → point at `.venv/bin/python`.

### API key

Two ways to provide your OpenRouter key:

- **Inline (quick).** Edit cell 2 in the notebook: `OPENROUTER_API_KEY = "sk-or-v1-..."`.
- **Env var (cleaner).** Export `OPENROUTER_API_KEY` in your shell before launching the notebook.

If you leave the variable as `None` and there's no env var, the notebook will prompt you with a hidden-input password field on first run.

### Choosing a model

The default is `anthropic/claude-haiku-4.5` — cheap, fast, more than capable for the tutorial. To switch, change `MODEL_SLUG` in cell 4. Anything OpenRouter exposes works:

```python
MODEL_SLUG = 'openai/gpt-5-mini'
MODEL_SLUG = 'google/gemini-2.5-flash'
MODEL_SLUG = 'deepseek/deepseek-r1'   # reasoning model
```

## Known Jupyter quirks (and the workarounds we apply)

The notebook applies two workarounds for issues that **only appear when running in a Jupyter notebook** (Cursor, VS Code Jupyter, classic Jupyter, or Colab). Plain `python script.py` doesn't need them.

### Workaround #1 — `nest_asyncio.apply()`

Jupyter has a running asyncio event loop for UI events. PydanticAI's `run_sync()` tries to start its own — without `nest_asyncio` you'd get:

```
RuntimeError: This event loop is already running.
```

The setup section installs and applies `nest_asyncio` as the first thing. It patches asyncio to allow nested event loops.

### Workaround #2 — explicit `httpx.AsyncClient`

When `async with agent.run_mcp_servers():` exits under `nest_asyncio`, the cleanup occasionally closes the httpx client that `OpenAIProvider` shares across every agent built from the same `MODEL`. After that, every agent call fails with:

```
pydantic_ai.exceptions.ModelAPIError: Connection error.
Cause: Cannot send a request, as the client has been closed.
```

The fix: own the httpx client ourselves and pass it via `http_client=`. PydanticAI then doesn't close it on context-manager exit. The setup cell does this:

```python
HTTPX_CLIENT = httpx.AsyncClient(timeout=60)
MODEL = OpenAIChatModel(
    MODEL_SLUG,
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.environ['OPENROUTER_API_KEY'],
        http_client=HTTPX_CLIENT,
    ),
)
```

### If you still hit a connection error

Easiest recovery: `Cmd+Shift+P` → **Jupyter: Restart Kernel and Clear All Outputs**, then **Run All** from the top.

## Stack

| Component | Choice |
|---|---|
| LLM access | OpenRouter (300+ models, OpenAI-compatible) |
| Agent framework | PydanticAI v1 (≥1.90) |
| Structured outputs | Pydantic v2 |
| Tool ecosystem | MCP (real servers via `MCPServerStdio`) |
| Mini-RAG | sentence-transformers (`all-MiniLM-L6-v2`) + numpy cosine similarity |
| Code execution | `subprocess` with timeout (production: E2B, Daytona, Modal — see `module_guide.pdf` §3.5) |


## Where to go next

After working through the notebook, the natural next steps are in the module guide:

- **Module 2.6 — Reasoning models** (when extended thinking actually helps)
- **Module 4 — Evals at scale** (instrument with Logfire / LangSmith / Langfuse)
- **Module 6 — Memory, computer use, voice** (Letta, Anthropic Computer Use, Pipecat)
- **Module 7 — Building safe agentic systems** (prompt injection, capability scoping, dual-LLM)

The pedagogical framework is adapted from Andrew Ng's *Agentic AI* course on DeepLearning.AI; the technical content has been brought up to May 2026.
