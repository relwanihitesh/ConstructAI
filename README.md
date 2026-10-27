# ConstructAI — Multimodal Construction Intelligence Platform

A complete local React + Vite frontend and FastAPI backend based on the supplied SkillWallet activities. Eight workflows, SQLite report history, JSON export, print-to-PDF, image validation, structured AI outputs, optional architectural concept generation, and an explicit no-key demo mode.

Cloud deployment: [Deploy on Render](https://render.com/deploy?repo=https://github.com/ikshitjain/ConstructAI). See [DEPLOY.md](DEPLOY.md) for the free demo configuration and storage limits.

## Sabse aasaan tareeka (Windows)

1. ZIP extract karein.
2. `ConstructAI/start.bat` double-click karein.
3. Pehli baar Python dependencies install hongi (internet required). Browser mein `http://127.0.0.1:8000` khulega.
4. Terminal window khuli rakhein. Band karne ke liye Ctrl+C.

Python 3.11+ required; tested here with Python 3.14. The ZIP includes a built frontend, so Node.js is only needed when changing/rebuilding the UI. Demo mode works without an API key. After initial dependency installation, demo workflows do not require internet; external Google fonts fall back to system fonts offline.

## Enable real AI

Copy `backend/.env.example` to `backend/.env`. Set:

```dotenv
GROQ_API_KEY=your_secret_key
AI_MODEL=qwen/qwen3.8-27b
POLLINATIONS_API_KEY=your_optional_secret_key
IMAGE_MODEL=flux
```

Restart the server. The status badge changes to **AI connected** when a key is configured; this indicates configuration, not verification of the provider account. An actual request validates key access and quota. Never put secret keys into frontend source or share `.env`.

Get a Groq key: https://console.groq.com/keys
Vision documentation: https://console.groq.com/docs/vision
The screenshot's Llama 4 Scout model has been retired for free/developer use. Model choice is configurable; the default follows the current vision documentation. See https://console.groq.com/docs/deprecations.
Pollinations secret keys: https://enter.pollinations.ai — optional, may require credits.
Image API reference: https://github.com/pollinations/pollinations/blob/main/gen.pollinations.ai/src/docs/quick-start.md

Real provider calls were not exercised during delivery because no API credentials were supplied. Integration success, provider failure, invalid output and vision payload handling are covered with mocked provider tests.

## Features and honest demo behavior

| Module | Demo mode | AI mode |
|---|---|---|
| Safety monitor | Validates image and creates inspection intake; no visual hazard assessment | Sends resized image + context for preliminary safety observations |
| Crack analysis | Inspection checklist; severity unknown | Preliminary visual observations and inspection recommendations |
| Project planner | Calculated budget, material allowances and phase sequence | Context-specific narrative; calculated metric cards retained |
| Property valuation | User rate × area, ±10% scenarios, gross rental yield | Contextual review with fixed calculated metric cards |
| Daily site assistant | Generic daily work checklist | Activity-specific work brief |
| Weather advisory | User conditions recorded; decision pending site review | Weather-sensitive activity advice based on entered conditions |
| Construction chat | Clearly labelled template response | Contextual answers with the last 12 conversation messages |
| Knowledge & documents | Structured document outline | Topic-specific method statement, checklist or toolbox talk draft |
| Concept studio | Disabled until image provider key is configured | Pollinations architectural rendering |

No live weather or property price data is fetched. Demo material coefficients are illustrative (cement 0.4 bag/sq ft, steel 4 kg/sq ft, sand 1.8 cu ft/sq ft, aggregate 1.35 cu ft/sq ft). They are not engineering quantities. Budget allocations are 45% structure/civil, 25% finishes, 15% services, 15% labour/overheads, plus a separately shown 10% contingency. Floor area is per storey and multiplied by storeys. Land, approvals, financing and taxes are excluded. Yield is annual gross rent / scenario value. These assumptions appear in generated reports.

## Developer setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r backend/requirements.txt
cd frontend
npm ci
npm run build
cd ..
.venv\Scripts\python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

For hot reload, keep backend on port 8000 and run `npm run dev` in `frontend`. Vite proxies `/api` to the backend. Build with `npm run build` after editing frontend code; the production backend serves `frontend/dist`. Use Node.js 20.19+ or 22.12+; tested with Node 24.

On macOS/Linux: `python3 launch.py` (or use `.venv/bin/python` in place of the Windows Python path).

## Architecture

```text
React UI → Axios → FastAPI routes → Pydantic input validation
                               → central AI handler → Groq vision/text API
                               → deterministic demo worksheets (no key)
                               → strict Report schema → SQLite → UI/export
Project planner → optional Pollinations image API → concept image
```

All report responses contain `title`, `summary`, `status`, `metrics`, `sections`, `limitations`, `mode`, `id`, `feature`, and `created`. Invalid AI JSON returns a clear 502 instead of fabricated default findings. Image uploads require JPEG/PNG/WebP, maximum 5 MB and 16 megapixels, and are re-encoded as JPEG up to 1600 px before transmission. Uploaded source images are not retained.

## API

- `GET /api/health` — mode and configured capabilities (no secrets)
- `POST /api/safety-monitor`, `/api/crack-detection` — multipart `image`, optional `text`
- `POST /api/project-planner` — location, area, floors, construction_type, rate, description
- `POST /api/real-estate-valuation` — location, area, rate, building_age, monthly_rent, amenities
- `POST /api/site-assistant` — activity, labour_count, site_condition
- `POST /api/weather-advisor` — activity, weather
- `POST /api/chatbot` — query, optional role/content history
- `POST /api/knowledge-base` — topic, document_type
- `POST /api/visualization` — prompt; returns image bytes
- `GET /api/history` — latest 100 reports
- `DELETE /api/history/{id}` — remove one saved report

Exact field constraints are available in Swagger `/docs`.

## Tests

```powershell
cd backend
python -m unittest test_app -v
```

Tests use a temporary database and fake provider responses. They exercise all eight modules, budget/yield math, invalid inputs, missing/corrupt/oversize images, history/deletion, missing image key, and real-AI adapter request/response contracts. Use the same virtual environment Python when testing an installation.

## Demo walkthrough

1. Overview → Project planner → keep example inputs → Generate demo report.
2. Confirm built-up area 2,400 sq ft and budget INR 5,808,000 (including 10% contingency).
3. Download JSON or choose Print, then Save as PDF in the browser print dialog.
4. Safety monitor → upload a JPEG/PNG → verify it is labelled Not assessed in demo mode.
5. Try Property valuation, Daily site assistant and Weather advisory.
6. Open Saved reports, revisit a report, or delete a disposable one.
7. Add API keys and restart for live AI / concept generation.

## Data, deployment and limitations

This is a local, single-user project, not an authenticated multi-tenant hosted service. It binds to localhost by default. Reports and submitted text are stored in `backend/data/reports.sqlite3`; deleting a report removes it from that database. Back up that file for persistence. Conversations are ephemeral in the UI, while individual generated responses and submitted context are saved as reports.

With a key configured, user text and resized images are sent to Groq. Concept prompts are sent to Pollinations. Keys remain server-side. Do not expose this app on a public interface before adding authentication, per-user authorization, TLS, request rate/body limits, retention policy, and deployment secrets management. For a future cloud deployment, run the FastAPI server with persistent storage and serve the compiled frontend from the same origin. No cloud deployment has been performed.

Outputs are educational planning aids, not structural certification, a regulatory inspection, a current market appraisal, or permission to execute hazardous work. Site professionals must review outputs. No precise crack measurements are inferred without appropriate scale and evidence. Generated concepts are not construction drawings.

## Troubleshooting

- Port 8000 occupied: close the previous ConstructAI terminal or run uvicorn on another port and visit that URL; update the Vite proxy only for development.
- AI 401/403: verify key and model permissions in backend/.env; restart.
- AI 429: provider quota/rate limit. Retry later or adjust your provider plan.
- AI 502: provider returned an error or invalid schema; retry. Demo results are never substituted silently.
- Image generation 503: configure POLLINATIONS_API_KEY and restart.
- Frontend changes not appearing: run npm run build, restart backend, and refresh.
- Dependency install failure: confirm internet access and Python version; run the pip command manually to see the error.
