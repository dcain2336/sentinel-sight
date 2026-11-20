# Sentinel Sight — Build Log

Entrant: dcain2336 (solo). Category 1, VALORANT Tactical Scouting. Deadline Jan 12, 2027 2:00 PM ET; submit Jan 10–11.
Plan: BUILD-PLAN.md. Brief: ENTRY-BRIEF.md. Repo: github.com/dcain2336/sentinel-sight (to be created, M1).
Hard rules: GRID data NEVER committed (public or private); $0 spend; no false attestations; pre-submit gates per contest_ops_hygiene.

## 2026-11-19 ~22:08 EST — M1 Agent B DONE (GRID data)
- Sparse checkout done: stl-hackathon-2026-grid-starter/ (VALORANT only, HEAD 496fa7f, 2.0 GB; ~33 min fetch). No data moved into the project repo.
- Series counts (val/series.csv): total 857 series / 2,078 games; GC NA 2025 = 107 (Split 1: 48, Split 2: 59; 268 games); VCT Americas 2025 = 106 (Kickoff 22, Stage 1 42, Stage 2 42).
- KEY FINDING: all 9 Cloud9 GC series are GC NA Split 2 2026 — ZERO in GC NA 2025. M2 seeded-opponent pick ("most series vs Cloud9 GC") needs 2026 data or a rethink.
- Chosen series 2833689 (YFP X vs Shopify Rebellion Gold, GC NA Split 2 2025 Playoffs, 2025-10-12, patch 11.07): 4,269 envelopes, 4,435 events, 2,086 player-used-ability, supplement join 2,086/2,086 (100%). Maps: Corrode 522, Abyss 674, Ascent 890 casts; 13 agents, 51 abilities; 225 placeable-utility casts; zero nulls.
- Sample files (gitignored data-samples/): casts_sample.json + casts_sample_summary.json. Script m1_stream.py (rerun: python3 m1_stream.py 2833689 full).
- Env: Python 3.12.3; zstandard 0.25.0 + duckdb 1.5.6 installed --user. $0 spent.
- M2 notes: add meta/ to sparse checkout (rosters.csv); agent resolved from snapshots; round time is wall-clock (pauses inflate it — refine in M2); map bounds in feed (Corrode x −6000..6000, y −7100..6500).
- Agent C spawned (maps + calibration + first heatmap) on B's sample data.

## 2026-11-19 ~21:32 EST — M1 Agent A DONE (repo)
- Repo live: https://github.com/dcain2336/sentinel-sight (public, main, created 21:31 EST, HTTP 201 first attempt).
- Commits pushed: 2480e9a (MIT LICENSE © 2026 David Scott Cain, .gitignore GRID block, README skeleton, scripts/check-push-clean.sh executable, ENTRY-BRIEF/BUILD-PLAN/BUILD-LOG) + b8967e6 (log entry).
- Push-clean check PASSED both times; verified via api.github.com (public, main, pushed_at 2026-11-20T02:31:51Z, 8 files).
- PAT handled transiently only (GIT_ASKPASS in /tmp, deleted after each push); no token in any file/log/report.
- Agent B (GRID data) still running.

## 2026-11-19 ~21:30 EST — M1 START (coordinator)
- Scott approved build start, no plan review needed.
- M1 scope: public repo + MIT license + GRID .gitignore + push-clean check; GRID sparse checkout next to project; map calibration spike; 1 real heatmap from real GRID data.
- Spawned in parallel: Agent A (GitHub repo + license + .gitignore + README skeleton), Agent B (GRID sparse checkout + series counts + one-series stream + ability-supplement join).
- Agent C (maps + calibration + first heatmap render) to spawn once B delivers sample cast positions.
- Open item (needs parent/browser task, NOT a generic subagent): JetBrains account creation (arc.agent.ops@gmail.com) + PyCharm Community + Air plugin + Junie Lite free-path verification. Sandbox has no desktop IDE; record outcome in docs/tooling-log.md when done.

## 2026-11-20 ~03:10 EST — M1 DATA FOUNDATION (Agent B)
- **GRID sparse checkout — DONE.** `git clone --filter=blob:none --sparse https://github.com/cloud9esports/stl-hackathon-2026-grid-starter stl-hackathon-2026-grid-starter && git sparse-checkout set val val-ability-supplements` (HEAD `496fa7f`). Top level: `AGENTS.md, LICENSE.md, README.md, val/, val-ability-supplements/` (no `lol/`, no `meta/`). `val/` = 858 entries (857 event files + `series.csv`); supplements = 857 entries (856 + README). Checkout is 2.0 GB on disk; the sparse-checkout fetch took ~33 min at ~30 MB/min (slow egress). Nothing decompressed to disk; no data file moved into the project repo.
- **Series counts** (from checked-out `val/series.csv`; verified identical to raw GitHub fetch by md5):
  - Total VALORANT series: **857**; total VALORANT games: **2,078** (counted from `meta/games.csv` via raw fetch — `meta/` is NOT in this sparse checkout; 3,817 games total incl. 1,739 LoL).
  - Game Changers NA 2025 (Split 1 + Split 2): **107** (Split 1: 48, Split 2: 59; 28 Playoffs, 79 Swiss; 268 games).
  - VCT Americas 2025: **106** (Kickoff 22, Stage 1 42, Stage 2 42).
  - Cloud9 / Cloud9 GC: 28 series mention Cloud9 (19× Cloud9 VCT Americas, 9× Cloud9 GC). **All 9 Cloud9 GC series are Game Changers NA Split 2 2026 — zero in GC NA 2025.** So no GC NA 2025 series features Cloud9 GC; the plan's M2 "most series vs Cloud9 GC" opponent pick will need 2026 data or a rethink.
  - Invalidated series `2855902` (Game Changers Pacific 2025, FENNEL HOTELAVA vs REIGNITE Lily) confirmed present in series.csv with an EMPTY ability_supplement field — the only series without one. Skip-handler is in the script.
  - Commands: `wc -l val/series.csv` (= 858 incl. header); `python3` csv counts with filters `event.startswith('Game Changers NA -') and '2025' in event`, `event.startswith('VCT Americas') and '2025' in event`, `'Cloud9 GC' in teams`.
- **Environment:** Python **3.12.3** (< 3.14, so stdlib zstd unavailable). Installed with `pip install --user --break-system-packages --no-cache-dir` (PEP 668; TMPDIR=`.../cloud9-jetbrains/.pip-tmp`): **zstandard 0.25.0**, **duckdb 1.5.6**. Git 2.43.0. $0 spent.
- **Chosen series: 2833689 — YFP X vs Shopify Rebellion Gold**, Game Changers NA Split 2 2025, Playoffs, 2025-10-12T21:00:00Z, patch 11.07. Why: no Cloud9 GC series exists in GC NA 2025, so per task fallback = any GC NA 2025 series; picked a late-season Playoff series (3 maps: Corrode, Abyss, Ascent; 58 rounds) with a known org (Shopify Rebellion Gold) for demo value. Supplement present.
- **Stream + join — DONE** (`m1_stream.py`, streams `.zst` via zstandard, never decompresses to disk):
  - Total: 4,269 envelopes, **4,435 events**. Top types: `player-used-ability` 2,086; `player-damaged-player` 1,181; `player-killed-player` 392; 58 rounds (`game-started-round` / `team-won-round` ×58).
  - `player-used-ability`: **2,086**; kept after rollback filter: 2,086. **Zero `!` rollback events in this series** (handler in place: `series-!started-game` → drop rolled-back game IDs).
  - Supplement rows: 2,264 (178 with `in_grid=false` — casts the GRID feed doesn't carry). **Joined: 2,086 / 2,086 (100%), 0 ability events without a supplement row.**
  - Distinct: 3 maps (Corrode 522 casts, Abyss 674, Ascent 890), 13 agents, 51 abilities, 10 players, 3 games, patch 11.07 only, sides attacker/defender. Placeable-utility casts (trapwire/trademark/sonic-sensor/gravnet/razorvine/barrier-mesh): 225. Date range UTC 2025-10-12 21:07:57–23:37:47.
  - **Zero nulls** in every output field (round, round time, agent, map, side, team). Round time 0.3–347.5s, no negatives.
- **Outputs (gitignored `data-samples/`, extracted data — NEVER commit):**
  - `data-samples/casts_sample.json` (2,086 casts; per cast: series/game id, map, patch, round number, side, team id, player, agent, ability slot/name, cast position x/y/z cm, aim direction, round time seconds).
  - `data-samples/casts_sample_summary.json` (counts + notes/caveats).
  - Script: `m1_stream.py` (`probe` / `full` modes; rerun: `python3 m1_stream.py 2833689 full`).
- **Data-shape findings (matter for M2 pipeline):**
  1. Agent/character is ABSENT from slim per-event player records; resolved by accumulating (game_id, player_id) → character from full snapshots across the stream. `meta/rosters.csv` is the alternate source — **M2 should add `meta` to the sparse-checkout set** (`git sparse-checkout add meta`) for rosters/games lookups.
  2. Round segments come in two shapes (full with `startedAt`, slim without); merge by sequenceNumber, keep startedAt once seen. Round number = segment sequenceNumber; round time = wall-clock seconds since segment startedAt.
  3. **Round-time caveat:** wall-clock, not game-clock — pauses inflate it (max 347.5s vs ~100s round). `game.clock.currentSeconds` is unusable at ability-event time (stuck at 0, jumps on sparse `game-set-gameClock` events). M2 refinement: use segment `duration` / pause-aware clock.
  4. Map bounds are in the feed (`map.bounds`, e.g. Corrode x −6000..6000, y −7100..6500) — Agent C calibration input.
- **Gitignore verified (Agent A, concurrent):** the repo `.gitignore` already carries the GRID block (`*.zst`, `*.jsonl`, `*.parquet`, `*.sqlite`, `*.duckdb`, `stl-hackathon-2026-grid-starter/`, `data-samples/`). `git status` shows only `BUILD-LOG.md` modified (this entry, uncommitted — left for Agent A/parent to commit) and `m1_stream.py` untracked (code, safe to commit). No data files tracked.
- **No blockers.** Repo reachable, supplement present for the chosen series, 100% join.

## 2026-11-20 ~03:20 EST — M1 CALIBRATION + FIRST HEATMAP (Agent C)
- **Map assets — DONE.** Fetched `https://valorant-api.com/v1/maps` (free, keyless, server-side); downloaded `displayIcon` (1024×1024) for Ascent, Corrode, Abyss into `app/public/maps/<uuid>.png` (bundled static assets, no live API call at demo time). Full API response saved at `docs/calibration/maps_api.json`.
- **Transform — VERIFIED, with a twist.** The API multipliers use **swapped axes**: `px = (y*xMultiplier + xScalarToAdd)*W`, `py = (x*yMultiplier + yScalarToAdd)*H` (displayIcon art is rotated 90° vs in-game minimap). The naive direct mapping was tested and REJECTED (15/22 Ascent callouts off-image). Values: Ascent (7e-05, -7e-05, 0.813895, 0.573242); Corrode (7e-05, -7e-05, 0.526158, 0.5); Abyss (8.1e-05, -8.1e-05, 0.5, 0.5).
- **Callout check (API callouts carry in-game coords; pass = lands on drawn art):** Ascent 22/22, Corrode 18/21 (3 A-side misses sit in wall/doorway gaps, not a systematic offset), Abyss 23/23. Direct transform: 2/22, 7/21, 14/23. Visual check in `docs/calibration/ascent-calibration.png` confirms every labelled point (Site A/B, both spawns, all mid callouts) lands on the right named location.
- **Residual error (multiplier vs independent bounds-fit from feed `map.bounds`):** Ascent median 2.0 px / p95 2.9 / max 3.2; Corrode 2.8 / 3.1 / 3.3; Abyss 31.6 / 57.1 / 71.4 (Abyss feed bounds extend past the drawn art, so the bounds-fit is the weaker method there — multiplier still validated by 23/23 callouts). All far below one heatmap cell (35.8 px). No fallback needed.
- **Cast coverage (real GRID casts, series 2833689):** 2,086/2,086 inside image; 2,065 on drawn art (Ascent 887/890, Corrode 518/522, Abyss 660/674). Off-art casts sit on map edges/doorways.
- **First heatmap — DONE:** `docs/calibration/ascent-heatmap-m1.png` — 890 Ascent casts, 500 cm bins (28×28 grid, ~35.8 px/cell), 209 non-empty cells, hottest cell 24 casts (B-site area). Cast positions only, not landing locations.
- **Environment note:** system matplotlib 3.6.3 is broken against user-site numpy 2.5.4 (compiled for numpy 1.x) — built an isolated venv `.venv-calib/` (matplotlib 3.11.2, numpy 2.5.5, pillow 13.0.0; `pip install` with TMPDIR under the work dir). `.venv-calib/` + `.pip-tmp/` added to `.gitignore`. $0 spent.
- **Script:** `scripts/calibrate_maps.py` (re-fetches API, re-verifies, re-renders both figures, rewrites `calibration_results.json`). Full note: `docs/calibration/README.md`.
- **Committed + pushed:** map PNGs, `docs/calibration/*`, `scripts/calibrate_maps.py`, Agent B's `m1_stream.py`, this log entry. Push-clean check PASSED; verified via api.github.com file listing (see below).
- **No blockers.** M1 exit criteria met: repo exists, 1 real heatmap on screen from real GRID data, calibration verified.

## 2026-11-19 ~21:31 EST — M1 repo created (Agent A)
- Repo: https://github.com/dcain2336/sentinel-sight (public, created 2026-11-20 02:31 UTC / 2026-11-19 21:31 EST, default branch main).
- Initial commit 2480e9a pushed to main: LICENSE (MIT, © 2026 David Scott Cain), .gitignore (GRID block: *.zst/*.jsonl/*.parquet/*.sqlite/*.duckdb, stl-hackathon-2026-grid-starter/, data-samples/, plus node_modules/, dist/, .env), README.md skeleton, scripts/check-push-clean.sh (executable), ENTRY-BRIEF.md, BUILD-PLAN.md, BUILD-LOG.md.
- Push-clean check: PASSED (no GRID data files tracked) before push.
- Push verification: api.github.com/repos/dcain2336/sentinel-sight confirms public, default_branch main, pushed_at 2026-11-20T02:31:32Z; tree lists all 7 files + scripts/check-push-clean.sh.
- Second commit (this log entry) pushed to main.
