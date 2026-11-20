# Cloud9 x JetBrains — Category 1 Build Plan: "Sentinel Sight"

**Entrant:** David Scott Cain (dcain2336), solo
**Hackathon:** Sky's The Limit Hackathon 2026 — https://cloud9.devpost.com/
**Category:** 1 (VAL/GC) — VALORANT Tactical Scouting, Utility Placement & Operator Profiler (picked Nov 19, 2026)
**Deadline:** January 12, 2027, 2:00 PM ET (11:00 AM PT)
**Prize (Category 1):** Best of Category $6,000 + GDC trip; Runner-up $2,000; Bonus Best AI-Powered Workflow Story $1,000
**Status:** PLAN — research verified live Nov 19–20, 2026. No repo created, nothing submitted, $0 spent.
**Companion file:** `ENTRY-BRIEF.md` (registration, eligibility, prizes, deliverables — already verified; not re-verified here)

---

## 1. What the official pages actually require (Category 1)

Source: https://cloud9.devpost.com/details/submission-specifics (read Nov 20, 2026, 01:00 UTC) and https://cloud9.devpost.com/ (same time).

**The job, in the organizers' words:** "Build an automated tactical scouting tool using a JetBrains tool that helps Cloud9's VALORANT and Game Changers coaches reduce manual VOD review by visualizing opponent utility and weapon tendencies." The tool "should be intuitive and require little to no technical expertise to interpret, think clear heatmaps, simple filters, and direct, actionable insights."

**Blueprints — own innovation explicitly allowed:** "Entrants can follow one of two featured blueprints (or combine them): a Utility Placement & Ability Analysis Engine or an Operator Tendency & Sniper Profiler, or build their own pro-tier scouting innovation." Combining the two is explicitly permitted.

**Blueprint A — Utility Placement & Ability Analysis Engine.** "Analyze opponent data to visualize where specific abilities are used. Priority should be given to 'Placeable' utility (e.g., Cypher trapwires, Killjoy alarm bots, Vyse walls, Chamber trips), followed by recon, smokes, reactive stall, and flashes."

**Blueprint B — Operator Tendency & Sniper Profiler.** "Track the economy and positioning of high-impact weapons like the Operator (or the Odin). The tool could identify how often a team buys or possesses the weapon, which specific agent/player is using it, and visually map where they set up on defense (e.g., pinpointing if a player prefers aggressive forward angles vs. passive pixel-angles) and whether Operator possession tends to shift between players or agents."

**Core capabilities the page lists (all are "could", not "must"):**
- Dynamic filtering by opponent team, map, player, agent, composition, patch, side, weapon, or specific ability.
- Coach-friendly visualizations: heatmaps with color gradients (light/dark density) or hard numbers (e.g., "75/100 rounds").
- Show the evidence behind tendencies: sample size, number of rounds/matches analyzed, event frequency.

**"Take it to the next level" (optional, high judging value):**
- Generate anti-strat solutions for Cloud9 (e.g., suggest a lineup/strategy to clear a heavily trapped zone).
- Self-scouting: apply the same analysis to Cloud9's own historical matches.

**What judges look for (Category 1):** "Your submission must demonstrate at least one useful, data-backed tactical insight for Cloud9 and show supporting evidence (e.g., sample size, number of rounds analyzed). Instead of a chat-bot prompt format, design your tool so coaches may derive the following insights visually:
- 'Opponent A most often (60%) uses their Sentinel utility at Point (X, Y) on Map B.'
- 'Team C's primary Operator player holds aggressive angles at Location D, 80% between 0-20s in the round, and only 10% between 20-40s.'"

**Data note that shapes the whole build:** "GRID provides the player's location and time when an ability is cast, but does not explicitly provide the ability's final landing location. Participants may explore creative inference or enrichment techniques, but exact landing-location reconstruction is not required." — i.e., cast-position heatmaps are sufficient; do not burn weeks on landing reconstruction.

**Global requirements (same page):** at least one JetBrains tool (IDE, JetBrains Air, or Junie); other editors may be used alongside. Submission must include: working project link/build, public code repo, demo video (≤3 min, public YouTube), methodology write-up, tooling explanation (which JetBrains tools, what each did). Devpost also encourages committing `.idea`, `.junie`, or `.air` folders as evidence of JetBrains-tool use.

**Judging criteria (https://cloud9.devpost.com/):** Technological Implementation (JetBrains-tool use, non-trivial working implementation), Design, Potential Impact, Quality of the Idea, Presentation.

---

## 2. GRID data — what it is, what it contains, license rules

Source: https://github.com/cloud9esports/stl-hackathon-2026-grid-starter (README read in full Nov 20, 2026). Access: public GitHub repo, linked from the Devpost resources page ("Official Esports Data GRID Hackathon Data Access").

**Coverage (2025–2026 seasons):**
- VALORANT: **857 series, 2,078 games** — VCT Americas (Kickoff/Stage 1/Stage 2 2025), VALORANT Masters Toronto 2025, and Game Changers (NA, BR, LATAM, EMEA, JPN, KR, Pacific, SEA, Oceania, plus Game Changers Championship 2025). Cloud9 appears as **Cloud9** (VCT Americas) and **Cloud9 GC** (Game Changers).
- League of Legends: 745 series, 1,739 games (LCK, LEC, LTA North/South, LCS) — not needed for Category 1.
- Ability supplements: **856 files** (one per VALORANT series, except the invalidated one) — see below.

**Format:**
- One compressed JSON Lines file per series: `val/events_{seriesId}_grid.jsonl.zst`. Each line is an envelope (`occurredAt`, `sequenceNumber`, `events[]`); event types read as sentences: `{actor}-{action}-{target}` (e.g., `player-used-ability`, `player-killed-player`, `team-won-round`, `player-completed-plantBomb`). A `!` reverses an earlier event (must handle rollbacks, e.g. `series-!started-game` for abandoned/replayed maps).
- `seriesState` is a full snapshot after each event (teams, games, players with `position`, `inventory`, `abilities`, `currentHealth`); the last event holds the final box score.
- Positions are `{x, y}` in game units — **centimetres in VALORANT**; each game's `map.bounds` gives the playable area.
- `meta/` CSVs (teams, players, characters, games, rosters, tournaments) — small lookup tables; IDs are unique only within a title, join on `(title, id)`. Player names are in-game nicknames only.
- `val/series.csv` indexes every match (event, stage, date, teams, file path, supplement path).
- **VALORANT ability supplement** (`val-ability-supplements/{seriesId}.jsonl.zst`): for each ability cast, the caster's 3D position, aim direction, and velocity at the exact moment, interpolated from movement samples (~5/sec; 1/sec in VCT Americas 2025). Joins to the GRID feed on `grid_event_id` = the `player-used-ability` event's id. This is the dataset Blueprint A is built on.

**Size / handling:** full repo ~1.4 GB (no file over 3 MB); uncompressed ~160 GB for VALORANT alone. **Stream `.zst` files, never decompress to disk.** Sparse checkout for VALORANT only: `git clone --filter=blob:none --sparse … && git sparse-checkout set val val-ability-supplements`. Python 3.14+ has stdlib zstd (`from compression import zstd`); on 3.13 or older, `pip install zstandard`.

**License — hard rules (from the repo README "License in plain words" + LICENSE.md):**
- ✅ Use the data to build, demo, and submit the hackathon project, **during the hackathon**.
- ✅ Share with your own team, show results/charts/demos to judges. ✅ Use AI assistants/coding agents on it — **if a tool lets you opt out of training on or retaining inputs, you must turn that on** (relevant to Junie/Air settings — do this on day one).
- ❌ **No redistribution** — never commit any data file (or decompressed/extracted copies: `.zst`, `.jsonl`, `.parquet`, `.sqlite`, `.duckdb`, `meta/` copies) to the project repo, public **or private**. Clone the data repo *next to* the project, point code at it via `STL_DATA_DIR`, and add the GRID `.gitignore` block. Before every push run: `git ls-files | grep -Ei '\.(zst|jsonl|parquet|sqlite|duckdb)$|stl-hackathon-2026-grid-starter'` — must print nothing. If data was ever committed, rewrite history (`git filter-repo`) before pushing; deleting in a later commit is not enough.
- ❌ No commercial use, including betting. ❌ No use for any other project after the hackathon ends.
- Copyright: GRID feeds © GRID eSports GmbH and Riot Games, Inc.; supplements/meta/docs © 2026 Cloud9 Esports, Inc. Aggregates, charts, screenshots, and computed results **are** fine to commit.
- **Data caveats to design around:** not every scheduled match is present (bracket gaps); a few series have abandoned/replayed maps (drop rolled-back game IDs); occasional feed gaps (derive results from per-game state, don't assume a complete feed); team names change between events — join on team IDs, not names; **one invalidated series: `2855902`** (Game Changers Pacific 2025) — feed holds only a rolled-back game start, no match data; times are UTC.

**Map images (not in the GRID repo):** GRID gives coordinates, not map art. Source: valorant-api.com — free, keyless community API (`https://valorant-api.com/v1/maps`), maps endpoint returns splash art, minimaps (`displayIcon`), and callouts with in-game coordinates, plus `xMultiplier` / `yMultiplier` / `xScalarToAdd` / `yScalarToAdd` for the game-coordinate → image transform. Assets remain Riot property; fan project, not endorsed by Riot. CORS is not enabled — fetch server-side at build time and **bundle the downloaded map images as static assets** in the repo (no live API call at demo time). Calibration step (Milestone 1): verify the transform by plotting known callout coordinates and a sample of cast positions; bin heatmaps into grid cells so small calibration error is invisible.

---

## 3. Blueprint comparison and recommendation

| | Blueprint A — Utility Placement Engine | Blueprint B — Operator Profiler |
|---|---|---|
| **Core data** | GRID feeds + ability supplement (3D cast position + aim + velocity) — the richest, most distinctive dataset in the starter repo | GRID feeds only (inventory, kills, positions) — computable from basic event types any entrant can do |
| **Output shape** | Heatmaps on map images + hard frequencies ("75/100 rounds") — exactly the visual the judges' example insights describe | Buy-rate stats + setup maps + round-timing distributions (0–20s vs 20–40s) |
| **Fit to ARC strengths** | Direct hit: Python ETL over large event streams, precomputed aggregates, dashboard + canvas heatmaps, free static hosting | Also dashboard-shaped, but thinner |
| **Demo punch (3 min)** | High — a heatmap appearing on a map is instantly legible on camera | Medium — statistics need narration to land |
| **Evidence / sample size** | Strong: hundreds of ability casts per team/map; thin-filter warnings still apply | Weaker: Operator rounds are a minority of rounds, so samples thin fast when filtered by map + player + side |
| **Anti-strat upside** | Concrete: "heavily trapped zone → suggest lineup to clear it" is a rule layer on the same data | Real but narrower: "don't peek D in first 20s" |
| **Scope risk** | Landing-location inference explicitly NOT required — the hardest sub-problem is off the table by rule | Low scope risk, but lower ceiling |

**Recommendation: Blueprint A as the primary build, Blueprint B as a stretch second tab.**

The spec explicitly allows combining both blueprints, and the two share the same pipeline (event stream → per-team/map aggregates), the same map/filter/heatmap components, and the same evidence panel. Build A to demo-ready first; add the Operator tab only after A is complete, seeded, and videoed. If time runs short, ship A alone — it is a complete, judges-shaped entry on its own.

**Product name: Sentinel Sight** — a VALORANT / Game Changers utility-scouting tool. (Sentinel = the utility class the engine prioritizes; Sight = the visualization.)

**Real user:** a VALORANT or Game Changers assistant coach / analyst — e.g., a Cloud9 GC analyst prepping for a match. **The unglamorous workflow it improves:** the night before a match, instead of scrubbing 3–5 hours of opponent VOD to log where their Sentinel puts trapwires and alarm bots and where their smokes land, the analyst opens Sentinel Sight, picks opponent + map, and gets a one-page visual: a heatmap of placeable utility with frequencies, sample size, and a suggested counter-lineup. That is the spec's own goal — "reduce manual VOD review" — delivered as a tool, not a chatbot.

**The one insight the demo must prove (judges require at least one data-backed tactical insight for Cloud9, with evidence):** a named, computed statement in the form "Opponent A most often (X%) uses their Sentinel utility at Point (X, Y) on Map B — n = N rounds across M matches." The exact opponent/map/numbers are computed during Milestone 2 from `meta/games.csv` (pick the opponent with the most series vs Cloud9 GC in Game Changers NA 2025 — verified from the data at build time, never guessed) and are frozen as the seeded demo.

---

## 4. Scope

### MVP (must ship — this is the entry)
1. **Ingestion pipeline (Python):** stream selected GRID series + ability supplements → per-(opponent team, map, agent, ability, side) aggregates: cast positions binned to grid cells, round counts, frequencies, sample sizes. Output: static JSON aggregates committed to the repo (aggregates are legal to commit).
2. **Utility heatmap view:** map image + canvas heatmap of placeable utility (Cypher trapwires, Killjoy alarm bots, Vyse walls, Chamber trips first; then smokes, recon, flashes), with hard numbers per cell ("42/56 rounds, 75%").
3. **Filters:** opponent team, map, agent, ability, side, patch — all client-side over the precomputed aggregates. Every filter combination shows its sample size; below a threshold (n < 10 rounds) the UI says so plainly instead of implying a pattern.
4. **Evidence panel:** for every insight shown — rounds analyzed, matches analyzed, event count, date range, patch range.
5. **Anti-strat suggestions (rule-based):** for the top 2–3 trapped zones per map, a suggested counter (e.g., "Sova recon + Breach stun to clear B-main trap cluster; 75% of rounds trapped"). Rules hand-written from the data, labeled as suggestions, not predictions.
6. **Self-scout tab (thin):** the same heatmap view pointed at Cloud9 / Cloud9 GC's own utility — the spec's second "next level" item, cheap once the components exist.
7. **Static hosting + seed/reset:** one-click seeded demo dataset (fixed opponent + map), reset button restores it, zero dead buttons.

### Stretch (only after MVP is demo-ready and videoed)
8. **Operator tab (Blueprint B):** buy/possession rate by player/agent, defense setup map (aggressive forward vs passive pixel angles), round-timing split (0–20s / 20–40s), possession-shift tracking. Reuses map/filter/heatmap components.
9. **Bonus prize — Best AI-Powered Workflow Story ($1,000):** short case study or short video on how Air/Junie accelerated the build. Cheap if session notes and screenshots are captured as you go; decide in Milestone 4. Submit as a URL alongside the main entry.

### Out of scope (do not build)
- Live data / live API calls at runtime or in the demo. All data is precomputed; the demo runs entirely offline-capable.
- Landing-location reconstruction (explicitly not required).
- User accounts, logins, or a backend server. Static site only.
- Any LoL functionality (Category 2 is a different entry).
- Betting, odds, or win-probability claims. No predictions presented as fact.

---

## 5. Tech stack — $0 only

| Layer | Choice | Why / cost |
|---|---|---|
| Data pipeline | Python 3.13 + `zstandard` (pip) + DuckDB (build-time aggregation) | Free; streams `.zst` without decompressing; DuckDB handles 857-series-scale aggregation locally. Python version note: README recipes target 3.14 stdlib zstd; 3.13 + `pip install zstandard` is the documented fallback. |
| Aggregates | Static JSON files committed to the repo | Legal per GRID license (aggregates/charts OK); zero runtime cost; demo cannot 429. |
| Frontend | Vite + TypeScript (no UI framework), hand-rolled CSS design system, HTML Canvas heatmaps | Minimal dependency surface for the 5-minute clean-clone test; canvas heatmap is the star, not a framework. Map images bundled as static assets (downloaded at build time from valorant-api.com). |
| Hosting | Cloudflare Pages (free tier) via ARC's proven `deploy.sh` / wrangler path | $0; ARC has a working deploy pipeline. Static site = no server cost, no cold starts in the demo. |
| Repo | Public GitHub repo, `github.com/dcain2336/<repo>` (create during Milestone 1), MIT license at root | Required by Devpost: public repo + open-source license file at root. |
| Maps/assets | valorant-api.com `/v1/maps` (free, keyless) at build time only | See §2. |
| Version control | Git; commit `.idea`, `.junie`, `.air` folders (Devpost encourages this as JetBrains-use evidence) | Free. |

**Nothing in this stack costs money. No paid APIs, no paid hosting, no subscriptions.** The only licenses involved are the JetBrains trial codes (free, §6) and the GRID data license (§2).

---

## 6. JetBrains tool plan — load-bearing, feature by feature

The sponsor rule (standing): the sponsor's newest capability must be load-bearing and documented feature-by-feature. JetBrains Air is this year's featured tool; Junie is the AI coding agent; the IDEs are the workbench. Each tool below has a named, non-decorative job, and the submission's Tooling Explanation will list exactly this table.

### Phase 1 — now until the codes land (~Nov 26): free/community tooling only
| Tool | Cost now | Exact job |
|---|---|---|
| **PyCharm Community** (free) | $0 | Python ETL development: GRID stream parsing, DuckDB aggregation, aggregate JSON generation. Its database view inspects the DuckDB aggregates. |
| **IntelliJ IDEA Community** (free) | $0 | Fallback/secondary IDE if PyCharm Community hits a limit; also the host for Air if PyCharm's Air plugin lags. |
| **JetBrains Air plugin** (free, EAP) | $0 | **The agent workspace.** Runs Junie Lite sessions, orchestrates parallel agent tasks (ETL vs frontend), IDE-native review of every agent diff before accept. Install from JetBrains Marketplace (2026.2+) or use the 2026.3 EAP build where Air is bundled. |
| **Junie Lite** (free with a JetBrains account, fair use) | $0 | The coding agent inside Air. Implements the ETL pipeline, the heatmap renderer, and the test suite, in bounded tasks with human review of each diff. **Caveat to verify at setup:** Junie Lite is free with a JetBrains account sign-in; the AI Free tier (3 credits/30 days) is reportedly not available in Community editions, so Junie Lite via Air is the free path — confirm on first run and record the outcome. |
| **JetBrains account** (free) | $0 | Required for Junie Lite/Air sign-in. Create with the ARC email (arc.agent.ops@gmail.com) — no JetBrains account exists yet. |

### Phase 2 — when the codes land (~Nov 26, emailed within 5 business days of Nov 19 registration)
| Tool | Cost | Exact job (switch from Phase 1) |
|---|---|---|
| **All Products Pack code (2 months)** | $0 (trial) | Unlocks **WebStorm** (frontend: Vite/TS app, built-in preview, testing, refactoring) and **PyCharm Professional** (replaces Community for the ETL; adds full database tooling instead of DataGrip). Activate the day the email lands; record activation date. |
| **AI Ultimate code (2 months)** | $0 (trial) | Unlocks **full Junie** (not just Lite) and AI Assistant inside the IDEs. Full Junie takes the heavier tasks: the anti-strat rule engine, the Operator tab, the test suite. Note the rules caveat (ENTRY-BRIEF.md): AI Ultimate needs an IDE/All Products Pack license or trial/EAP to activate; student licenses are not valid — the All Products Pack code satisfies this. |
| **JetBrains Air (continued)** | $0 | Same orchestration role, now driving full Junie instead of Lite; parallel sessions for frontend + ETL. |

**Rules for the tooling story (keep the bonus-prize case study cheap):**
- Keep a dated log (one file, `docs/tooling-log.md`) of what each tool did each week — Air sessions, Junie tasks accepted/rejected, WebStorm/PyCharm features used. This log becomes the Bonus Prize case study with almost no extra work.
- Screenshot Air's session review and Junie diffs as you go; store under `docs/tooling-evidence/`.
- **GRID license interaction:** the starter repo README requires opting out of training/retention on AI-tool inputs where the tool allows it. Set that in Junie/Air settings on day one and note it in the tooling log.
- **Pin versions once the build starts.** Air is EAP with frequent updates — do not upgrade mid-build unless a fix is needed; record the IDE + Air + Junie versions in the README.

---

## 7. Data pipeline design (the part that wins or loses this)

1. **Select series:** from `val/series.csv`, all Game Changers NA 2025 series (Split 1 + Split 2, ~107 series) plus VCT Americas 2025 for Cloud9 self-scouting. Verify counts from the file at build time; record them in the README with the command used.
2. **Stream + join:** for each series, stream `val/events_*.jsonl.zst`, keep `player-used-ability` events (and `player-killed-player` / inventory events for the Operator stretch), join to `val-ability-supplements/{id}.jsonl.zst` on `grid_event_id`. Handle `!` rollback events (drop rolled-back game IDs) and skip invalidated series `2855902`.
3. **Normalize:** per cast — opponent team id, map, game id, round number, side, agent, ability (slot + name), cast position (x, y, z), aim direction, round time (seconds since round start, from `round-started-freezetime` / round clock), patch (from `meta/games.csv`).
4. **Aggregate (DuckDB):** bin cast positions into grid cells per map (calibrated to map image via §2 transform); compute per (team, map, agent, ability, side): casts, rounds with ≥1 cast, total rounds, frequency %, plus round-time distribution (0–20s / 20–40s / 40s+). Emit one JSON per (team, map) + a manifest with totals, date range, patch range, series count.
5. **Validate:** every aggregate carries its own evidence (rounds, matches, events). A build-time check fails the build if any shipped aggregate has n < 10 rounds without the UI's low-sample flag — the check, not a human, enforces honesty.
6. **Seed dataset:** the demo ships with one fixed opponent + two maps preloaded (opponent chosen in Milestone 2 for maximum series count vs Cloud9 GC). A `seed` script regenerates the aggregates deterministically from the data repo; `reset` restores the shipped seed in the UI.

**Coordinate calibration (Milestone 1, do not skip):** GRID positions are centimetres with per-game `map.bounds`; valorant-api.com maps carry `xMultiplier/yMultiplier/xScalarToAdd/yScalarToAdd` and callouts with in-game coordinates. Verify the transform by plotting 3+ known callouts and a sample of cast positions on the map image; if the transform is off, fall back to a linear fit from `map.bounds` to image pixels. Binning into grid cells (not pixel-exact points) makes residual error invisible.

---

## 8. App design

**Screens (single-page app, tabs):**
1. **Scout (default):** opponent picker → map picker → heatmap canvas with ability/agent filter chips → frequency readout per cell on hover/click ("Cypher Trapwire — B Main: 42/56 rounds, 75%") → evidence panel (rounds, matches, events, date range, patch).
2. **Anti-Strat:** top 3 trapped zones for the selected map + a suggested counter per zone (rule-based, labeled "suggestion"), each linked back to its heatmap cell.
3. **Self-Scout:** same Scout view pointed at Cloud9 / Cloud9 GC.
4. **Operator (stretch tab):** buy/possession rate, setup map, round-timing split, possession shifts.

**Design requirements (from the spec):** clear heatmaps (color gradient + hard numbers), simple filters, direct actionable insights, no technical expertise needed to read it. No chatbot UI — the spec explicitly says "instead of a chat-bot prompt format."

**Demo-readiness rules (standing):** seeded data, reset button, zero dead buttons — every visible control does something real or is not rendered.

---

## 9. Milestones — now to January 12, 2027

| Window | Milestone | Exit criteria |
|---|---|---|
| **Nov 20–26** | **M1 — Foundation (free tooling).** Create public GitHub repo + MIT license + GRID `.gitignore` block + push-clean check. Install PyCharm Community + Air plugin + Junie Lite; verify Junie Lite free path and record it. Sparse-checkout GRID data repo next to the project. Map calibration spike: one series streamed end-to-end, 1 heatmap rendered on a real map image. | Repo exists; 1 real heatmap on screen from real GRID data; calibration verified. |
| **Nov 26–Dec 6** | **M2 — Codes + core pipeline.** Activate All Products Pack + AI Ultimate the day the email lands; switch frontend to WebStorm, ETL to PyCharm Pro. Build the full pipeline (§7) over GC NA 2025 + VCT Americas 2025. Choose the seeded opponent (most series vs Cloud9 GC) and compute the one named insight for the demo. | Aggregates generated with evidence fields; the named insight computed with real numbers (record date + command). |
| **Dec 7–20** | **M3 — App + anti-strat.** Scout view, filters, evidence panel, anti-strat suggestions, self-scout tab. Seed/reset wired. First full end-to-end run on Cloudflare Pages. | Deployed demo link works from a clean clone + `npm install` + build; every button does something. |
| **Dec 21–Jan 5** | **M4 — Stretch + video + write-ups.** Operator tab if M3 is solid (else cut it — A alone is a complete entry). Demo video (see §10). Methodology write-up, tooling explanation, README with Limitations, bonus workflow-story decision. | Video recorded; write-ups drafted; anti-slop grep clean. |
| **Jan 6–11** | **M5 — Pre-submit gates + submit.** Run all §12 gates. Submit on Devpost **Jan 10–11** (not the last day) so a form surprise has a buffer day. | Submission live; all deliverable URLs verified by opening them fresh. |
| **Jan 12, 2:00 PM ET** | Deadline. | Nothing left to do. |

**Buffer note:** ShepherdCare's final submit is Nov 27 and Reddit Game of the Day's deadline is Dec 8 — M1/M2 overlap those. Keep Cloud9 work to the M1 spike until Dec 8 is past, then go full-time on M2/M3. The Jan 12 deadline still leaves ~5 clear weeks.

---

## 10. Demo plan (≤3 min YouTube, public)

- **Seeded data only. No live API calls mid-demo.** The deployed site loads precomputed JSON; map images are bundled. Rehearse twice with the exact demo inputs (fixed opponent + map).
- **0:00–0:30 — real core action first:** open the deployed site, pick the seeded opponent and map, the heatmap appears, click the hottest cell: "Cypher trapwire at B Main — 42 of 56 rounds, 75%, across 14 matches." That is the product in 30 seconds.
- **0:30–1:30 — filters + evidence:** switch agent/ability/side filters live, show the sample-size readout changing, open the evidence panel.
- **1:30–2:15 — anti-strat + self-scout:** show one counter-suggestion and the Cloud9 self-scout view.
- **2:15–2:50 — weak spot named on camera:** say plainly that heatmaps show where utility was *cast from*, not where it landed (GRID does not provide landing locations; the spec says reconstruction is not required), and that tendencies are 2025–2026 data, so a patch can age them.
- **2:50–3:00 — close on the real output:** the one named insight, on screen, with its evidence.
- **Operator tab (if built):** 15 seconds inside the 1:30 block, or cut — never let the stretch crowd out the core.
- Scott on camera is not required for this entry (no such rule found); a narrated screen recording is the format. If Scott prefers to appear, the narration script is the same.

---

## 11. Risks and honest limitations

1. **Cast position ≠ landing location.** GRID records where the player was standing and aiming when an ability was cast, not where it landed. Heatmaps show cast origins; a smoke's landing zone is inferred, not measured. Mitigation: label every heatmap "cast positions" and say so in the video and README. The spec explicitly does not require landing reconstruction.
2. **Data is 2025–2026 and frozen.** No live feed exists in the starter repo, so tendencies reflect past patches and rosters; a 2027 patch or roster move can age an insight. Mitigation: every view shows its date range and patch range; the README states the coverage window.
3. **Thin samples on deep filters.** Filtering to one opponent + one map + one agent + one side can drop below 10 rounds, where a "75%" is noise. Mitigation: the evidence panel always shows n, and the UI flags low-sample views instead of hiding the number.
4. **Map-coordinate calibration is approximate.** The GRID-centimetre → map-image transform comes from a community API's multipliers, not an official spec. Mitigation: grid-cell binning (not pixel points) plus the Milestone 1 calibration check against known callouts; residual error is smaller than a cell.
5. **Operator tab is scope risk.** It is explicitly a stretch item; cutting it loses nothing from the primary entry.

---

## 12. Pre-submit gates (standing, from contest_ops_hygiene)

Run all of these in Milestone 5, before submitting — no exceptions:
- **5-minute clean-clone test:** fresh clone, README Quick Start only, timed. If it fails, the README is the bug.
- **Anti-slop grep:** 0 hits on the ban list (see `~/workspace/custom-skills/contest_ops_hygiene/SKILL.md`); deletion test on every paragraph of the description/methodology.
- **Limitations section:** the README carries §11 (2–4 honest limits + what would fix each). Do not soften them for the submission.
- **Real numbers only:** every number in the submission (series counts, round counts, frequencies) comes from a real run, with date + reproducing command recorded. No invented stats.
- **Seed + reset + zero dead buttons:** seeded demo loads on first open; reset restores it; every visible control works.
- **Demo video:** rehearsed twice with exact demo inputs, seeded data, real core action in the first 30 seconds, weak spot named on camera, ends on real output.
- **JetBrains load-bearing:** the Tooling Explanation documents each tool's job from §6; `.idea` / `.junie` / `.air` committed as evidence.
- **GRID hygiene:** the pre-push `git ls-files` check from §2 prints nothing; no secrets in repo, logs, or screenshots.
- **RLS/security:** no backend, no user data — nothing to secure; state that in the README rather than leaving it unaddressed.

---

## 13. Submission checklist (Devpost "Enter a Submission")

From https://cloud9.devpost.com/details/submission-specifics and https://cloud9.devpost.com/:
- [ ] Public repo URL (GitHub) with source + assets + run instructions + open-source license at root
- [ ] Working demo link (Cloudflare Pages URL) — or judge-accessible build
- [ ] Text description: features + which JetBrains tools were used and what each did
- [ ] Methodology write-up: approach + how the tool solves the category's problem
- [ ] Demo video: ≤3 min, public on YouTube
- [ ] Category: 1 (VAL/GC)
- [ ] Bonus prize URL (workflow story) — only if M4 decides yes
- [ ] At least one data-backed tactical insight for Cloud9, with evidence, demonstrable in the tool

---

## 14. Sources (all verified live Nov 19–20, 2026)

- Category 1 requirements, blueprints, judging: https://cloud9.devpost.com/details/submission-specifics
- Hackathon overview, prizes, criteria: https://cloud9.devpost.com/
- Resources (JetBrains tools, GRID link): https://cloud9.devpost.com/resources
- GRID starter data repo (coverage, format, license, caveats): https://github.com/cloud9esports/stl-hackathon-2026-grid-starter
- JetBrains Air (free plugin, Junie Lite free with JetBrains account): https://blog.jetbrains.com/ai/2026/10/getting-started-with-air-part1/ and https://blog.jetbrains.com/webstorm/category/news/feed/ (WebStorm 2026.3 release notes)
- valorant-api.com (free, keyless maps API): https://valorant-api.com/
- Registration, eligibility, prizes, deliverables: see `ENTRY-BRIEF.md` (verified Nov 19, 2026 — not re-verified here)
