# Sentinel Sight

VALORANT / Game Changers utility scouting tool — see where utility actually lands, not where the playbook says it should.

**Hackathon:** Cloud9 × JetBrains "Sky's The Limit" Hackathon 2026 — Category 1
**Deadline:** January 12, 2027, 2:00 PM ET (submit January 10–11)
**Status:** Milestone 1 — in progress

## Stack

Python + DuckDB ETL → static JSON → Vite / TypeScript + Canvas heatmaps, hosted on Cloudflare Pages ($0).

## Quick Start

> Placeholder — commands will be filled in as the app lands.

```bash
# ETL (Python + DuckDB) — builds static JSON aggregates from GRID data (local only, never committed)
# TODO: python etl/build_aggregates.py

# App (Vite + TypeScript)
# TODO: cd app && npm install && npm run dev
```

## Limitations

> Placeholder — to be filled with honest, measured limits once the first heatmap lands (see BUILD-PLAN.md §B3 pre-submit gates).

## GRID data license note

Match data comes from the GRID hackathon dataset (`stl-hackathon-2026-grid-starter/`), licensed for hackathon use only. Raw and extracted GRID data is **never committed** to this repo — only small derived aggregates (static JSON) are published. See `.gitignore` and `scripts/check-push-clean.sh`.
