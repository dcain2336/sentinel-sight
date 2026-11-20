# Map calibration — Milestone 1

**Verdict: CALIBRATION VERIFIED.** The valorant-api.com multiplier transform
(with swapped axes — see below) places real GRID cast positions on the right
named locations on all three maps in the sample. First real heatmap:
[`ascent-heatmap-m1.png`](ascent-heatmap-m1.png).

## Method

Map art (`displayIcon`, 1024×1024 PNG) and transform constants come from
`https://valorant-api.com/v1/maps` (free, keyless, fetched server-side at
build time 2026-11-20; full response saved as `maps_api.json`). Images are
bundled as static assets in `app/public/maps/<map-uuid>.png` — no live API
call at demo time. Map art remains Riot property; fan-project use.

**Transform (winner): API multipliers, axes swapped.** Game Y drives image X
and game X drives image Y (the displayIcon art is rotated 90° vs the
in-game minimap orientation):

```
px = (y * xMultiplier + xScalarToAdd) * W
py = (x * yMultiplier + yScalarToAdd) * H
```

The naive direct mapping (`px` from game `x`, `py` from game `y`) was tested
and rejected: it puts 15/22 Ascent callouts off-image entirely.

| Map | UUID | xMultiplier | yMultiplier | xScalarToAdd | yScalarToAdd |
|---|---|---|---|---|---|
| Ascent | 7eaecc1b-4337-bbf6-6ab9-04b8f06b3319 | 7e-05 | -7e-05 | 0.813895 | 0.573242 |
| Corrode | 1c18ab1f-420d-0d8b-71d0-77ad3c439115 | 7e-05 | -7e-05 | 0.526158 | 0.5 |
| Abyss | 224b0a95-48b9-f703-1bd8-67aca101a61f | 8.1e-05 | -8.1e-05 | 0.5 | 0.5 |

## Callout check (API callouts carry in-game coordinates)

A callout "passes" when its transformed pixel lands on drawn (opaque) map
art; the Ascent figure [`ascent-calibration.png`](ascent-calibration.png)
also confirms each labelled point visually (Site A in the A-site zone,
Site B in the B-site zone, both spawns, all mid callouts — all correct).

| Map | Swapped transform | Direct transform (rejected) |
|---|---|---|
| Ascent | 22/22 on art | 2/22 on art (15 off-image) |
| Corrode | 18/21 on art | 7/21 on art |
| Abyss | 23/23 on art | 14/23 on art |

Corrode's 3 misses (Crane A, Lobby A, Main A) land 1–2 px off the drawn art
in wall/doorway gaps on A side — single-point callouts in narrow corridors,
not a systematic offset: Corrode casts still land 518/522 on art.

## Residual error (multiplier vs independent bounds-fit fallback)

Second method: linear fit from the GRID feed's per-game `map.bounds`
(Ascent x −4850..7550, y −11100..2200 cm; Corrode x −6000..6000,
y −7100..6500; Abyss x −6000..6000, y −6800..5800) to the opaque-art
bounding box of the image. Displacement between the two transforms, over
the real casts of each map:

| Map | Median | p95 | Max |
|---|---|---|---|
| Ascent | 2.0 px | 2.9 px | 3.2 px |
| Corrode | 2.8 px | 3.1 px | 3.3 px |
| Abyss | 31.6 px | 57.1 px | 71.4 px |

Ascent/Corrode: the two independent methods agree to ~3 px — far below one
heatmap cell (35.8 px). Abyss disagrees more because its feed bounds extend
past the drawn art (void edges), so the bounds-fit is the weaker method
there; the multiplier is still validated by 23/23 callouts and 660/674
casts on art. **No fallback needed: multiplier transform wins on all maps.**

## Cast coverage (real GRID casts, series 2833689)

| Map | Casts | Inside image | On drawn art |
|---|---|---|---|
| Ascent | 890 | 890 (100%) | 887 (99.7%) |
| Corrode | 522 | 522 (100%) | 518 (99.2%) |
| Abyss | 674 | 674 (100%) | 660 (97.9%) |
| **Total** | **2,086** | **2,086** | **2,065 (99.0%)** |

Off-art casts (21 total) sit on map edges / in doorways — consistent with
cast positions being where a player stood, including half-in-wall spots,
not with a transform error.

## Heatmap — [`ascent-heatmap-m1.png`](ascent-heatmap-m1.png)

- **Data:** 890 Ascent ability casts, series 2833689 (YFP X vs Shopify
  Rebellion Gold, Game Changers NA Split 2 2025 Playoffs), patch 11.07,
  2025-10-12. All 890 plotted; 0 outside the image.
- **Binning:** 500 cm cells → 28×28 grid, ~35.8 px per cell (binning, not
  pixel-exact points, so the ~3 px residual error is invisible).
- **Counts:** 209 non-empty cells; hottest cell 24 casts (B-site area).
  Gradient: inferno, 0–24 casts per cell.
- **Reading:** this is a CAST-position heatmap — where players stood when
  they used an ability, not where the ability landed (GRID does not record
  landing locations; the spec says reconstruction is not required).
- Round time was NOT used for this spike (wall-clock, pauses inflate it —
  see BUILD-LOG.md).

## Reproduce

```bash
.venv-calib/bin/python scripts/calibrate_maps.py
# venv: python3 -m venv .venv-calib && .venv-calib/bin/pip install matplotlib pillow numpy
```

Re-fetches the maps API, re-downloads art only if missing, re-verifies
callouts + casts, re-renders both figures, rewrites
`calibration_results.json` (machine-readable numbers behind this note).

## Files in this folder

- `README.md` — this note
- `ascent-calibration.png` — callout verification figure (Ascent)
- `ascent-heatmap-m1.png` — first real heatmap (Ascent, 890 casts)
- `calibration_results.json` — all numbers above, machine-readable
- `maps_api.json` — raw valorant-api.com `/v1/maps` response (2026-11-20)
