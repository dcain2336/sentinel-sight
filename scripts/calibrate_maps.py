#!/usr/bin/env python3
"""Sentinel Sight — Milestone 1 map calibration spike.

Fetches map art + transform constants from valorant-api.com (free, keyless),
verifies the GRID-centimetre -> map-image transform against the API's own
callouts (which carry in-game coordinates), renders the first real heatmap
from Agent B's sample casts, and writes the calibration figures + note.

Key finding (verified 2026-11-20): the API multipliers use SWAPPED axes —
game Y drives image X and game X drives image Y:

    px = (y * xMultiplier + xScalarToAdd) * W
    py = (x * yMultiplier + yScalarToAdd) * H

The naive direct mapping (game X -> image X) puts 15/22 Ascent callouts
off-image entirely. The swapped mapping puts 22/22 Ascent callouts on the
drawn map art, and 890/890 Ascent casts inside the image (887/890 on art).

Fallback checked: a linear fit from the GRID feed's per-game map.bounds to
the opaque-art bounding box of the image. It agrees with the multiplier
transform to a median of ~10 px (see results JSON) — well under one heatmap
cell (~36 px at the 500 cm bin size) — so the multiplier transform wins and
no fallback is needed.

Inputs (NOT committed, gitignored):
    data-samples/casts_sample.json   (Agent B, series 2833689)
    stl-hackathon-2026-grid-starter/ (GRID sparse checkout, for map.bounds)
Outputs (committed — aggregates / charts, legal per GRID license):
    app/public/maps/<uuid>.png       (bundled map art, Riot property, fan use)
    docs/calibration/maps_api.json   (API response, transform constants)
    docs/calibration/ascent-calibration.png
    docs/calibration/ascent-heatmap-m1.png
    docs/calibration/calibration_results.json
    docs/calibration/README.md       (written by hand from the results)

Usage:  .venv-calib/bin/python scripts/calibrate_maps.py
        (venv: python3 -m venv .venv-calib && .venv-calib/bin/pip install matplotlib pillow numpy)
"""
import json
import math
import os
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MAPS_API = "https://valorant-api.com/v1/maps"
MAPS_DIR = ROOT / "app" / "public" / "maps"
CAL_DIR = ROOT / "docs" / "calibration"
CASTS_PATH = ROOT / "data-samples" / "casts_sample.json"

# Maps in Agent B's sample (series 2833689). uuid -> display name.
TARGET_MAPS = {
    "7eaecc1b-4337-bbf6-6ab9-04b8f06b3319": "Ascent",
    "1c18ab1f-420d-0d8b-71d0-77ad3c439115": "Corrode",
    "224b0a95-48b9-f703-1bd8-67aca101a61f": "Abyss",
}

# GRID feed map.bounds for series 2833689 (extracted from
# val/events_2833689_grid.jsonl.zst, actor.state.games[].map.bounds).
# x/y in centimetres. Used only for the fallback-fit comparison.
FEED_BOUNDS = {
    "ascent": {"x": (-4850.0, 7550.0), "y": (-11100.0, 2200.0)},
    "corrode": {"x": (-6000.0, 6000.0), "y": (-7100.0, 6500.0)},
    "abyss": {"x": (-6000.0, 6000.0), "y": (-6800.0, 5800.0)},
}

BIN_CM = 500  # heatmap bin size (cm); ~36 px on the 1024 px image


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def transform_multiplier(loc, m, W, H, swapped=True):
    """API multiplier transform. swapped=True is the verified form."""
    if swapped:
        px = (loc["y"] * m["xMultiplier"] + m["xScalarToAdd"]) * W
        py = (loc["x"] * m["yMultiplier"] + m["yScalarToAdd"]) * H
    else:
        px = (loc["x"] * m["xMultiplier"] + m["xScalarToAdd"]) * W
        py = (loc["y"] * m["yMultiplier"] + m["yScalarToAdd"]) * H
    return px, py


def opaque_bbox(alpha):
    ys, xs = np.where(alpha > 10)
    return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())


def transform_bounds_fit(loc, bounds, bbox, W, H):
    """Fallback: linear fit from feed map.bounds to the opaque-art bbox.

    Axes are swapped the same way (game Y -> image X, game X -> image Y);
    image Y decreases as game X increases (yMultiplier is negative).
    """
    (bx0, bx1), (by0, by1) = bounds["x"], bounds["y"]
    x0, x1, y0, y1 = bbox
    px = (loc["y"] - by0) / (by1 - by0) * (x1 - x0) + x0
    py = (1.0 - (loc["x"] - bx0) / (bx1 - bx0)) * (y1 - y0) + y0
    return px, py


def on_art(px, py, alpha, W, H):
    return 0 <= px < W and 0 <= py < H and alpha[int(py), int(px)] > 10


def main():
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    CAL_DIR.mkdir(parents=True, exist_ok=True)

    api = fetch_json(MAPS_API)
    assert api["status"] == 200, api.get("status")
    (CAL_DIR / "maps_api.json").write_text(json.dumps(api, indent=1))
    by_uuid = {m["uuid"]: m for m in api["data"]}

    casts = json.loads(CASTS_PATH.read_text())
    results = {"maps": {}, "method": "multiplier-swapped", "bin_cm": BIN_CM}

    for uuid, name in TARGET_MAPS.items():
        m = by_uuid[uuid]
        img_path = MAPS_DIR / f"{uuid}.png"
        if not img_path.exists():
            download(m["displayIcon"], img_path)
        im = Image.open(img_path).convert("RGBA")
        W, H = im.size
        arr = np.array(im)
        alpha = arr[:, :, 3]
        bbox = opaque_bbox(alpha)

        entry = {
            "uuid": uuid,
            "displayIcon": m["displayIcon"],
            "image_size": [W, H],
            "xMultiplier": m["xMultiplier"],
            "yMultiplier": m["yMultiplier"],
            "xScalarToAdd": m["xScalarToAdd"],
            "yScalarToAdd": m["yScalarToAdd"],
            "opaque_bbox": list(bbox),
            "feed_bounds_cm": FEED_BOUNDS[name.lower()],
        }

        # --- callout verification, both orientations ---
        for label, swapped in (("swapped", True), ("direct", False)):
            inside = on = 0
            misses = []
            for c in m["callouts"]:
                px, py = transform_multiplier(c["location"], m, W, H, swapped)
                if 0 <= px < W and 0 <= py < H:
                    inside += 1
                    if on_art(px, py, alpha, W, H):
                        on += 1
                    else:
                        misses.append(c["regionName"])
            entry[f"callouts_{label}"] = {
                "inside": inside, "on_art": on, "total": len(m["callouts"]),
                "misses": misses,
            }

        # --- cast coverage (swapped) + method disagreement ---
        sub = [c for c in casts if c["map"] == name.lower()]
        inside = on = 0
        disps = []
        for c in sub:
            p = c["cast_position_cm"]
            px, py = transform_multiplier(p, m, W, H, True)
            if 0 <= px < W and 0 <= py < H:
                inside += 1
                if on_art(px, py, alpha, W, H):
                    on += 1
            fx, fy = transform_bounds_fit(p, FEED_BOUNDS[name.lower()], bbox, W, H)
            disps.append(math.hypot(px - fx, py - fy))
        disps = np.array(disps)
        entry["casts"] = {
            "total": len(sub), "inside_image": inside, "on_art": on,
            "outside_image": len(sub) - inside,
        }
        entry["multiplier_vs_bounds_fit_px"] = {
            "median": round(float(np.median(disps)), 1),
            "mean": round(float(np.mean(disps)), 1),
            "p95": round(float(np.percentile(disps, 95)), 1),
            "max": round(float(np.max(disps)), 1),
        }
        results["maps"][name] = entry
        print(f"{name}: callouts swapped "
              f"{entry['callouts_swapped']['on_art']}/{entry['callouts_swapped']['total']} on-art; "
              f"casts {on}/{len(sub)} on-art; "
              f"method disagreement median {entry['multiplier_vs_bounds_fit_px']['median']} px")

    # --- Ascent calibration figure (callout check) ---
    m = by_uuid["7eaecc1b-4337-bbf6-6ab9-04b8f06b3319"]
    im = Image.open(MAPS_DIR / "7eaecc1b-4337-bbf6-6ab9-04b8f06b3319.png").convert("RGBA")
    W, H = im.size
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(im)
    picks = ["Site A", "Site B", "Spawn Attacker Side", "Spawn Defender Side",
             "Top Mid", "Bottom Mid", "Main A", "Main B", "Window A", "Boat House B",
             "Market Mid", "Catwalk Mid"]
    for c in m["callouts"]:
        label = f"{c['regionName']} {c['superRegionName']}".strip()
        px, py = transform_multiplier(c["location"], m, W, H, True)
        ax.plot(px, py, "o", ms=7, mfc="red", mec="white", mew=1.2, zorder=5)
        if label in picks:
            ax.annotate(label, (px, py), fontsize=8, color="white",
                        xytext=(6, 6), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.6, ec="none"),
                        zorder=6)
    ax.set_title("Ascent calibration — API callouts via swapped multiplier transform\n"
                 "22/22 callouts land on drawn map art (red dots)", fontsize=11)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(CAL_DIR / "ascent-calibration.png", dpi=150)
    plt.close(fig)

    # --- Ascent heatmap (500 cm bins over the map image) ---
    asc = [c for c in casts if c["map"] == "ascent"]
    xs = np.array([(c["cast_position_cm"]["y"] * m["xMultiplier"] + m["xScalarToAdd"]) * W
                   for c in asc])
    ys = np.array([(c["cast_position_cm"]["x"] * m["yMultiplier"] + m["yScalarToAdd"]) * H
                   for c in asc])
    # 500 cm in pixels: |multiplier| * 1024 * 500
    bin_px = abs(m["xMultiplier"]) * W * BIN_CM
    nx = max(1, int(W // bin_px)); ny = max(1, int(H // bin_px))
    grid, _, _ = np.histogram2d(ys, xs, bins=[ny, nx],
                                range=[[0, H], [0, W]])
    results["heatmap"] = {
        "map": "Ascent", "casts_plotted": len(asc),
        "bin_cm": BIN_CM, "bin_px": round(float(bin_px), 1),
        "grid_cells": [ny, nx], "nonempty_cells": int((grid > 0).sum()),
        "max_cell_casts": int(grid.max()),
        "casts_inside_image": int(((xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)).sum()),
    }
    # Display the binned counts directly (no smoothing: the bins ARE the data)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(im)
    ax.imshow(np.ma.masked_where(grid == 0, grid), cmap="inferno", alpha=0.75,
              extent=[0, W, H, 0], interpolation="nearest", zorder=4)
    sm = plt.cm.ScalarMappable(cmap="inferno",
                               norm=plt.Normalize(vmin=0, vmax=grid.max()))
    cb = fig.colorbar(sm, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("ability casts per 500 cm cell", fontsize=10)
    ax.set_title("Ascent — ability cast heatmap (M1)\n"
                 "890 casts · series 2833689 (YFP X vs Shopify Rebellion Gold)\n"
                 "GC NA Split 2 2025 Playoffs · patch 11.07", fontsize=10)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(CAL_DIR / "ascent-heatmap-m1.png", dpi=150)
    plt.close(fig)

    (CAL_DIR / "calibration_results.json").write_text(json.dumps(results, indent=1))
    print(json.dumps(results["heatmap"], indent=1))
    print("DONE — figures in", CAL_DIR)


if __name__ == "__main__":
    main()
