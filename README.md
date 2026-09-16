# Waypoint

[![CI](https://github.com/willapat/langchain-job-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/willapat/langchain-job-tracker/actions/workflows/ci.yml)

A job application tracker with a LangGraph agent at its center — not bolted on the side. Paste a job posting link or description and the agent fetches it, extracts the structured fields, asks you about anything important it couldn't find, and saves it. Ask it questions about your pipeline. Tell it to delete something and it will ask for your approval first, every time.

![Waypoint board view](docs/screenshots/board.png)

## Why this exists

This started as a small project to learn LangChain/LangGraph — a CLI that could save, list, update, and delete job applications through a chat loop. This version keeps that agent (same middleware, same tools, same guardrails) and puts a real product around it: a FastAPI backend on SQLite, a REST API for the parts of the UI that should be instant (dragging a card, jotting a note), and a React frontend with a kanban board and analytics.

The interesting design decision is *where* the agent sits. Kanban drag-and-drop and note-taking talk to the REST API directly — routing a card drag through an LLM would just make the UI feel broken. But adding an application from a link or description, answering questions about your pipeline, and deleting anything all go through the agent, because those are exactly the tasks an LLM is good at (extraction, summarization) or where a second opinion matters (irreversible actions).

## Features

- **Kanban board** — five-stage pipeline (Applied → Screening → Interview → Offer / Rejected), drag-and-drop with optimistic updates, keyboard-accessible status changes, per-column scrolling so a big "Applied" column doesn't blow out the page.
- **Agent-powered ingestion** — paste a job posting URL or description into the assistant. It fetches the page (with SSRF-guarded server-side fetching), extracts company/role/salary/location/requirements, and **asks a follow-up question** if something important is missing rather than silently saving nulls.
- **Chat assistant** — ask about your applications in plain language ("what's in my interview stage?"), update statuses, or delete an application. Responses stream token-by-token over SSE.
- **Human-in-the-loop deletion** — deleting an application always surfaces an approve/reject card in the chat before anything happens. This is `HumanInTheLoopMiddleware` from LangChain's agent framework, not custom code.
- **Analytics** — total/active counts, response and interview rates, pipeline breakdown, applications-over-time chart, and an "Ask the assistant" button that sends the agent your actual numbers and asks it to find concrete patterns (e.g. rejections clustering around a specific seniority or role type) instead of generic advice.
- **Notes & interview prep** — a per-application timeline for freeform notes and interview log entries.
- **Topic guardrail** — the agent refuses off-topic requests ("what's the weather?") and stays on job-tracking.
- **SQLite persistence** — real schema (`Application`, `Note`) via SQLAlchemy, not a flat JSON file.

## Screenshots

| Board | Analytics |
|---|---|
| ![Board](docs/screenshots/board.png) | ![Analytics](docs/screenshots/analytics.png) |

**Agent-mediated deletion**, asking for approval before touching the database:

![Chat approval flow](docs/screenshots/chat_approval.png)

## Architecture

```mermaid
flowchart LR
    subgraph Browser
        UI[React + Vite\nBoard / Analytics / Chat]
    end

    subgraph Backend["FastAPI (app/)"]
        REST[REST routers\napplications · notes · stats]
        Chat[Chat router\nSSE streaming]
        Agent[LangGraph agent\nagents/job_agent.py]
        MW[Middleware:\nTopicGuardrail → prompt →\nSummarization → HumanInTheLoop]
        Tools[Tools\ntools/job_tools.py]
        Fetch[SSRF-guarded fetcher\n+ structured extraction]
    end

    DB[(SQLite\njobs.db)]

    UI -- "drag/drop, notes, stats\n(instant, no LLM)" --> REST
    UI -- "chat + agent-routed ingest" --> Chat
    Chat --> Agent
    Agent --> MW --> Tools
    Tools --> Fetch
    Tools --> DB
    REST --> DB
```

**Why the split:** REST for anything that should feel instant and deterministic (status changes, notes, reading data); the agent for anything that benefits from language understanding (extracting a posting, answering a question in plain English) or needs a safety check (deletion). `main.py` (the original CLI) and `langgraph dev` (LangGraph Studio) both build the agent from the same `agents/job_agent.py:build_agent()` factory as the web backend — there's one agent, three entry points.

## The agent, in more detail

`agents/job_agent.py` builds a `langchain.agents.create_agent` graph with middleware applied in this order:

1. **`TopicGuardrail`** (`middleware/guardrails.py`) — a `before_agent` hook that short-circuits off-topic requests before they reach the model at all. Deliberately keyword-based and deliberately simple; it excludes generic words like "what" or "show" from its allow-list because those appear in off-topic questions too ("what's the weather?") and would defeat the block.
2. **A dynamic system prompt** — personalizes the assistant and, importantly, spells out the multi-step ingestion workflow (fetch → extract → review → ask if something's missing → save) so the model doesn't just dump partial data into the database.
3. **`SummarizationMiddleware`** — keeps long conversations from blowing the context window.
4. **`HumanInTheLoopMiddleware`** — configured with `interrupt_on={"delete_application": True}`, so any call to the delete tool pauses the graph and surfaces an approval request instead of executing.

Seven tools (`tools/job_tools.py`): `save_application`, `get_applications`, `update_status`, `delete_application`, `fetch_job_posting` (SSRF-guarded URL fetch), `extract_job_fields` (structured extraction *without* saving — the model decides whether to ask a follow-up before calling `save_application` itself), and `get_pipeline_stats` (exact aggregate numbers for the feedback feature, so the model cites real counts instead of estimating from a raw list).

**A few correctness details worth calling out**, because each one silently produced wrong behavior rather than an obvious error:

- `HumanInTheLoopMiddleware`'s reject decision uses the `message` field *verbatim* as the tool's result if you provide one. If your UI passes a bare user-typed reason ("changed my mind") as that message, the model never learns the delete was actually blocked — it only sees an ambiguous string — and can hallucinate "I've deleted it" in its reply. Both the CLI and the web chat panel compose the reject message as `"...tool was NOT executed. Reason given: {reason}"` specifically to avoid this.
- The board matches an application's status against its five lowercase columns by exact string. The agent sometimes saves a differently-cased status ("Applied" with a capital A) — that write succeeds, the data is fine, it just never matches any column and never renders anywhere on the board. No error, just a card that silently doesn't exist visually. Fixed by normalizing status casing once, in `app/crud.py`, rather than trusting every caller (agent tool or REST) to send it consistently.
- The chat SSE client parses `event:`/`data:` frames by splitting on `"\n\n"`. The Vite dev proxy rewrites the backend's separators to `"\r\n\r\n"`, which that split never matches — every event was silently dropped, with the request still completing normally underneath. The chat panel just sat on its "thinking" indicator forever for what looked like a slow response but was actually a fully-completed, fully-discarded one. Found by comparing a raw `fetch()` against the same URL (which worked) to the app's own parser (which didn't), then normalizing CRLF to LF before parsing.

Both of the last two only surfaced when actually clicking through the running app, not from staring at the code — a reminder that "the tests pass" and "it works" aren't the same claim.

## Tech stack

**Backend:** Python, FastAPI, SQLAlchemy 2.x / SQLite, LangChain + LangGraph, `langchain-google-genai` (Gemini), httpx + BeautifulSoup for ingestion, `sse-starlette` for streaming, pytest.

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, `@dnd-kit` (drag-and-drop), Recharts, React Router, `react-markdown` (assistant replies render as formatted text, not raw `**`/`###`).

## Quickstart

Requires Python 3.11+, Node 20+, and a [Google Gemini API key](https://aistudio.google.com/apikey).

```bash
git clone <this-repo>
cd job-tracker
cp .env.example .env        # add your GOOGLE_API_KEY
make install                # python venv + pip install + npm install
make seed                   # populate jobs.db with demo data
make dev                    # backend on :8000, frontend on :5173
```

Open `http://localhost:5173`.

Other useful targets:

```bash
make cli      # the original terminal chat interface
make test     # pytest (backend) + tsc (frontend)
make build    # production frontend build
```

There's also `langgraph dev` (via `langgraph.json`) if you want to inspect the graph in LangGraph Studio.

## API reference

| Method & path | Purpose |
|---|---|
| `GET /api/applications` | List applications, optional `?status=` filter |
| `POST /api/applications` | Create manually (used by the "enter manually" fallback) |
| `PATCH /api/applications/{id}` | Partial update — this is what kanban drag-and-drop calls |
| `DELETE /api/applications/{id}` | Delete directly (no approval step — that's the agent path) |
| `GET/POST /api/applications/{id}/notes` | List / add notes |
| `PATCH/DELETE /api/notes/{id}` | Edit / remove a note |
| `GET /api/stats` | Status breakdown, applications-over-time, response/interview rates |
| `POST /api/chat` | Send a message to the agent; streams SSE (`token`, `interrupt`, `error`, `done`) |
| `POST /api/chat/resume` | Resolve a pending approval (`{"decisions": [{"type": "approve"}]}`) |
| `GET /api/chat/{thread_id}/state` | Rehydrate a conversation (and any pending approval) after a page reload |

## Testing

```bash
make test
```

41 tests covering: CRUD logic and status transitions, the guardrail's allow/deny behavior (including the off-topic-keyword-overlap edge case above), the SSRF validator's IP-range blocklist and JSON-LD-preferring extraction, tool return contracts, and the applications API. Agent responses that require a live Gemini call aren't asserted against in tests — those were verified manually end-to-end (delete → approve → confirmed in SQLite; delete → reject → confirmed *not* deleted; real Greenhouse posting → correct structured extraction).

CI (`.github/workflows/ci.yml`) runs this same suite plus a frontend build on every push and PR. It needs a `GOOGLE_API_KEY` env var to even *import* the backend (building the LangGraph agent constructs a Gemini client at module load time) — CI sets a placeholder since no test actually calls the model.

## Limitations & honest notes

- **Chat history is in-memory** (`InMemorySaver`) and resets on backend restart. Application data does not — that lives in SQLite. Swapping in `AsyncSqliteSaver` for persistent chat history is a natural next step.
- **Ingestion is best-effort on JS-heavy or login-walled sites.** Greenhouse/Lever/Ashby postings usually work well (many emit JSON-LD `JobPosting` data, which the fetcher prefers over scraping). LinkedIn and Indeed often don't — the agent will tell you and ask you to paste the description instead.
- **This is a single-user local app.** No auth, because there's one user (you), running it locally.
- **Model latency varies** (roughly 2–40s depending on whether the agent needs to call tools and reason about follow-up questions) — the chat panel shows a thinking indicator so it doesn't look frozen during that wait.
