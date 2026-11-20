#!/usr/bin/env python3
"""Sentinel Sight M1 — stream one GRID VALORANT series end-to-end.

Streams val/events_{seriesId}_grid.jsonl.zst (never decompresses to disk),
counts event types, handles `!` rollback events (drops rolled-back game IDs),
and joins player-used-ability events to the ability supplement on
grid_event_id. Writes casts_sample.json + summary JSON into data-samples/.

Usage: python3 m1_stream.py <series_id> [max_casts]
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import zstandard as zstd

WORK = Path(__file__).resolve().parent
DATA = WORK / "stl-hackathon-2026-grid-starter"
OUT = WORK / "data-samples"
INVALIDATED = {"2855902"}


def parse_ts(s):
    # "2025-01-16T22:14:03.512Z"
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read_jsonl_zst(path):
    with zstd.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def probe(series_id):
    """Print the structure of one player-used-ability event + one rollback
    event (if any) so field extraction can be verified before the full pass."""
    path = DATA / "val" / f"events_{series_id}_grid.jsonl.zst"
    n = 0
    for env in read_jsonl_zst(path):
        for e in env["events"]:
            if e["type"] == "player-used-ability" and n == 0:
                print("=== SAMPLE player-used-ability event ===")
                print(json.dumps(e, indent=2)[:4000])
                print("=== actor.state keys ===",
                      list((e.get("actor") or {}).get("state", {}).keys()))
                print("=== seriesState game keys ===")
                ss = e.get("seriesState") or {}
                games = ss.get("games") or []
                if games:
                    print(list(games[0].keys()))
                    print("map:", games[0].get("map"))
                    print("segments keys:",
                          list((games[0].get("segments") or [{}])[0].keys())
                          if games[0].get("segments") else None)
                n += 1
            if "!started-game" in e["type"] and n < 2:
                print("=== ROLLBACK event ===")
                print(json.dumps(e, indent=2)[:2500])
                n += 1
            if n >= 2:
                return


def stream_series(series_id, max_casts=None):
    if series_id in INVALIDATED:
        raise SystemExit(f"series {series_id} is invalidated (2855902) — skipping")
    path = DATA / "val" / f"events_{series_id}_grid.jsonl.zst"
    if not path.exists():
        raise SystemExit(f"missing feed file: {path}")
    sup_path = DATA / "val-ability-supplements" / f"{series_id}.jsonl.zst"

    type_counts = Counter()
    total_events = 0
    total_envelopes = 0
    rolled_back_games = set()
    rolled_back_events = 0
    ability_events = []          # raw player-used-ability events (pre-rollback filter)
    game_map = {}                 # game_id -> map name
    game_patch = {}               # game_id -> patch (titleVersion.name)
    game_rounds = {}              # game_id -> {round seq: startedAt or None}
    agent_map = {}                # (game_id, player_id) -> agent name; character
                                  # only appears in full snapshots, so accumulate
                                  # across the whole stream
    first_ts = last_ts = None

    for env in read_jsonl_zst(path):
        total_envelopes += 1
        ts = parse_ts(env["occurredAt"])
        first_ts = first_ts or ts
        last_ts = ts
        for e in env["events"]:
            total_events += 1
            etype = e["type"]
            type_counts[etype] += 1
            ss = e.get("seriesState") or {}
            # Track per-game map / patch / round segments from the snapshot.
            for g in ss.get("games") or []:
                gid = g.get("id")
                if not gid:
                    continue
                if (g.get("map") or {}).get("name"):
                    game_map[gid] = g["map"]["name"]
                tv = g.get("titleVersion") or {}
                if tv.get("name"):
                    game_patch[gid] = tv["name"]
                segs = g.get("segments") or []
                # Round segments come in two shapes: full (with startedAt)
                # and slim (id/sequenceNumber/teams/type only). Merge by
                # sequenceNumber, keeping startedAt once seen.
                rd = game_rounds.setdefault(gid, {})
                for s in segs:
                    if s.get("type") == "round" and s.get("sequenceNumber") is not None:
                        seq = s["sequenceNumber"]
                        if s.get("startedAt"):
                            rd[seq] = s["startedAt"]
                        elif seq not in rd:
                            rd[seq] = None
                for t in g.get("teams") or []:
                    for p in t.get("players") or []:
                        ch = p.get("character") or {}
                        cname = ch.get("name") if isinstance(ch, dict) else ch
                        if cname:
                            agent_map[(gid, p.get("id"))] = cname
            # Rollback: series-!started-game undoes a game start.
            if etype == "series-!started-game":
                tgt = e.get("target") or {}
                gid = tgt.get("id")
                if not gid:
                    # fall back to seriesStateDelta games list
                    delta = e.get("seriesStateDelta") or {}
                    for g in delta.get("games") or []:
                        gid = g.get("id")
                if gid:
                    rolled_back_games.add(gid)
            if etype == "player-used-ability":
                actor = e.get("actor") or {}
                astate = actor.get("state") or {}
                # game id: find the game whose team contains this player
                pid = actor.get("id")
                games = ss.get("games") or []
                game_id = None
                for g in games:
                    for t in g.get("teams") or []:
                        for p in t.get("players") or []:
                            if p.get("id") == pid:
                                game_id = g.get("id")
                                break
                        if game_id:
                            break
                    if game_id:
                        break
                # Round in progress AT THIS EVENT: the accumulated round
                # segments for this game (ability events carry only the slim
                # game object, no segments of their own — the running state
                # above is updated from every event's snapshot first).
                round_no = None
                round_started_at = None
                rd = game_rounds.get(game_id) or {}
                if rd:
                    round_no = max(rd)
                    round_started_at = rd.get(round_no)
                ability_events.append({
                    "event_id": e.get("id"),
                    "occurred_at": env["occurredAt"],
                    "game_id": game_id,
                    "player_id": pid,
                    "player_name": astate.get("name"),
                    "team_id": astate.get("teamId"),
                    "side": astate.get("side"),
                    "round_number": round_no,
                    "round_started_at": round_started_at,
                    "series_state": ss,
                })

    # Drop events belonging to rolled-back games.
    kept_ability = [a for a in ability_events
                    if a["game_id"] not in rolled_back_games]
    rolled_back_events = len(ability_events) - len(kept_ability)

    # ---- join supplement on grid_event_id ----
    supplement = {}
    sup_total = 0
    sup_not_in_grid = 0
    if sup_path.exists():
        for row in read_jsonl_zst(sup_path):
            sup_total += 1
            if not row.get("in_grid", True):
                sup_not_in_grid += 1
            supplement[row["grid_event_id"]] = row
    else:
        print(f"WARNING: supplement missing: {sup_path}")

    casts = []
    joined = 0
    missing_sup = 0
    for a in kept_ability:
        sup = supplement.get(a["event_id"])
        if sup is None:
            missing_sup += 1
            continue
        joined += 1
        ss = a["series_state"]
        game_id = a["game_id"]
        # agent (character) from the accumulated full-snapshot map
        # (character is absent from the slim per-event player records)
        player_name = a["player_name"]
        agent_name = agent_map.get((game_id, a["player_id"]))
        team_id = a["team_id"]
        side = a["side"]
        for g in ss.get("games") or []:
            if g.get("id") != game_id:
                continue
            for t in g.get("teams") or []:
                for p in t.get("players") or []:
                    if p.get("id") == a["player_id"]:
                        team_id = team_id or t.get("id")
                        side = side or t.get("side")
                        player_name = player_name or p.get("name")
                        if not agent_name:
                            ch = p.get("character") or {}
                            agent_name = ch.get("name") if isinstance(ch, dict) else ch
        # round number + round time: captured at event time from the
        # snapshot's round segments (round number = segment sequenceNumber;
        # round start = that segment's startedAt).
        rnd = a.get("round_number")
        rtime = None
        if a.get("round_started_at"):
            rtime = round((parse_ts(a["occurred_at"])
                           - parse_ts(a["round_started_at"])).total_seconds(), 3)
        pos = (sup.get("interpolated") or {}).get("position") or {}
        view = (sup.get("interpolated") or {}).get("view") or {}
        casts.append({
            "series_id": series_id,
            "game_id": game_id,
            "map": game_map.get(game_id),
            "patch": game_patch.get(game_id),
            "round_number": rnd,
            "side": side,
            "team_id": team_id,
            "player": player_name,
            "player_id": a["player_id"],
            "agent": agent_name,
            "ability_slot": sup.get("slot"),
            "ability": sup.get("ability"),
            "cast_position_cm": {"x": pos.get("x"), "y": pos.get("y"),
                                 "z": pos.get("z")},
            "aim_direction": {"x": view.get("x"), "y": view.get("y"),
                              "z": view.get("z")},
            "round_time_seconds": rtime,
            "occurred_at_utc": a["occurred_at"],
            "supplement_quality": sup.get("quality"),
        })
        if max_casts and len(casts) >= max_casts:
            break

    summary = {
        "series_id": series_id,
        "feed_file": f"val/events_{series_id}_grid.jsonl.zst",
        "supplement_file": f"val-ability-supplements/{series_id}.jsonl.zst",
        "total_envelopes": total_envelopes,
        "total_events": total_events,
        "event_type_counts": dict(type_counts.most_common()),
        "player_used_ability_events": len(ability_events),
        "player_used_ability_kept_after_rollback_filter": len(kept_ability),
        "rolled_back_game_ids": sorted(rolled_back_games),
        "rolled_back_ability_events_dropped": rolled_back_events,
        "supplement_rows": sup_total,
        "supplement_rows_not_in_grid_feed": sup_not_in_grid,
        "joined_ability_casts": joined,
        "ability_events_without_supplement_row": missing_sup,
        "casts_written": len(casts),
        "distinct_maps": sorted({c["map"] for c in casts if c["map"]}),
        "distinct_agents": sorted({c["agent"] for c in casts if c["agent"]}),
        "distinct_abilities": sorted({c["ability"] for c in casts if c["ability"]}),
        "distinct_players": sorted({c["player"] for c in casts if c["player"]}),
        "distinct_games": sorted({c["game_id"] for c in casts if c["game_id"]}),
        "distinct_patches": sorted({c["patch"] for c in casts if c["patch"]}),
        "distinct_sides": sorted({c["side"] for c in casts if c["side"]}),
        "date_range_utc": {
            "first_event": first_ts.isoformat() if first_ts else None,
            "last_event": last_ts.isoformat() if last_ts else None,
        },
        "round_time_basis": "seconds since the current round segment's "
                            "startedAt (seriesState games[].segments[] "
                            "type=round); round number = segment sequenceNumber",
        "invalidated_series_skipped": series_id in INVALIDATED,
    }
    return casts, summary


def main():
    if len(sys.argv) < 2:
        print("usage: m1_stream.py <series_id> [probe|full] [max_casts]")
        sys.exit(2)
    series_id = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    if mode == "probe":
        probe(series_id)
        return
    max_casts = int(sys.argv[3]) if len(sys.argv) > 3 else None
    casts, summary = stream_series(series_id, max_casts)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "casts_sample.json", "w", encoding="utf-8") as f:
        json.dump(casts, f, indent=2)
    with open(OUT / "casts_sample_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "event_type_counts"}, indent=2))
    print("event_type_counts:", summary["event_type_counts"])


if __name__ == "__main__":
    main()
