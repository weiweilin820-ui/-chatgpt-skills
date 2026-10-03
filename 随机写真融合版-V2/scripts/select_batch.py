#!/usr/bin/env python3
"""Select a semantically diverse portrait-plan batch from a JSON candidate pool.

The input is a JSON array of compact plan objects. This utility intentionally
does not compose prose; it chooses plans, assigns independently randomized
batch flags, and emits a machine-readable diversity audit.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import secrets
import sys
from typing import Any


REQUIRED_FIELDS = (
    "scene_domain",
    "spatial_archetype",
    "venue",
    "facility",
    "activity",
    "pose_family",
    "outfit_family",
    "top_silhouette",
    "bottom_silhouette",
    "material",
    "artistic_finish",
)

FINGERPRINT_FIELDS = (
    "scene_domain",
    "spatial_archetype",
    "venue",
    "activity",
    "outfit_family",
    "top_silhouette",
    "bottom_silhouette",
    "material",
    "artistic_finish",
)

OUTFIT_FIELDS = (
    "outfit_family",
    "top_silhouette",
    "bottom_silhouette",
    "material",
)

RATIOS = ("9:16", "4:5", "3:4", "1:1")
RATIO_WEIGHTS = (74.0, 15.0, 8.0, 3.0)

EMOTIONS = (
    "开心", "愉悦", "惊喜", "期待", "好奇", "俏皮", "得意", "害羞", "放松", "温柔", "释然",
    "平静", "专注", "若有所思", "克制", "警觉", "倔强", "冷淡", "怀疑", "困惑", "无奈", "恍惚",
    "疲惫", "憔悴", "失落", "悲伤", "难过", "委屈", "孤独", "怅然",
    "担忧", "紧张", "惊慌", "害怕", "震惊", "烦躁", "生气",
)

FORBIDDEN_SHOULDER_TERMS = ("单肩", "斜肩", "不对称肩", "单侧肩", "一字斜肩")
HOSIERY_FORM_TERMS = ("中筒", "及膝", "过膝", "大腿", "吊带", "连裤袜", "裤袜")
SHORT_HOSIERY_TERMS = ("短袜", "短筒", "船袜", "踝袜", "ankle sock", "ankle socks", "no-show sock", "no-show socks")
LONG_DENIM_TERMS = ("牛仔长裤", "丹宁长裤", "微喇牛仔", "直筒牛仔长裤", "破洞牛仔长裤")
LONG_TROUSER_TERMS = ("长裤", "微喇裤", "直筒裤", "机能长裤", "西装长裤", "牛仔长裤", "丹宁长裤")


def clean(value: Any) -> str:
    return " ".join(str(value).strip().split())


def normalized(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if not clean(candidate.get(field, ""))]
    if missing:
        raise ValueError(f"candidate {index} is missing: {', '.join(missing)}")
    result = dict(candidate)
    for field in REQUIRED_FIELDS:
        result[field] = clean(result[field])
    result["_candidate_index"] = index
    return result


def fingerprint(candidate: dict[str, Any]) -> tuple[str, ...]:
    return tuple(candidate[field] for field in FINGERPRINT_FIELDS)


def outfit_fingerprint(candidate: dict[str, Any]) -> tuple[str, ...]:
    return tuple(candidate[field] for field in OUTFIT_FIELDS)


def distance(left: dict[str, Any], right: dict[str, Any]) -> int:
    return sum(left[field] != right[field] for field in FINGERPRINT_FIELDS)


def has_forbidden_shoulder(candidate: dict[str, Any]) -> bool:
    text = " ".join(
        clean(candidate.get(field, ""))
        for field in ("outfit_family", "top_silhouette", "material")
    )
    return any(term in text for term in FORBIDDEN_SHOULDER_TERMS)


def is_long_denim(candidate: dict[str, Any]) -> bool:
    text = clean(candidate.get("bottom_silhouette", ""))
    return any(term in text for term in LONG_DENIM_TERMS)


def is_long_trouser(candidate: dict[str, Any]) -> bool:
    text = clean(candidate.get("bottom_silhouette", ""))
    return any(term in text for term in LONG_TROUSER_TERMS)


def has_short_hosiery(candidate: dict[str, Any]) -> bool:
    hosiery = clean(candidate.get("hosiery", "")).lower()
    return any(term.lower() in hosiery for term in SHORT_HOSIERY_TERMS)


def ambiguous_hosiery(candidate: dict[str, Any]) -> bool:
    hosiery = clean(candidate.get("hosiery", ""))
    if not hosiery or hosiery in {"裸腿", "无", "none", "None"}:
        return False
    if not any(token in hosiery for token in ("袜", "丝袜", "裤袜", "渔网")):
        return False
    return not any(term in hosiery for term in HOSIERY_FORM_TERMS)


def choose_rng(seed: str | None) -> random.Random:
    if seed is None:
        return secrets.SystemRandom()
    return random.Random(seed)


def score_candidate(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    field_counts: dict[str, Counter[str]],
    pose_counts: Counter[str],
    rng: random.Random,
) -> float:
    if selected:
        min_distance = min(distance(candidate, item) for item in selected)
        adjacent_distance = distance(candidate, selected[-1])
    else:
        min_distance = len(FINGERPRINT_FIELDS)
        adjacent_distance = min_distance

    rarity = sum(
        1.0 / (1.0 + field_counts[field][candidate[field]])
        for field in FINGERPRINT_FIELDS
    )
    pose_bonus = 2.5 / (1.0 + pose_counts[candidate["pose_family"]])
    return min_distance * 12.0 + adjacent_distance * 4.0 + rarity + pose_bonus + rng.random()


def select(candidates: list[dict[str, Any]], count: int, rng: random.Random) -> list[dict[str, Any]]:
    if count < 1:
        raise ValueError("count must be positive")
    if len(candidates) < count:
        raise ValueError(f"need at least {count} candidates, received {len(candidates)}")

    unique: dict[tuple[str, ...], dict[str, Any]] = {}
    for item in candidates:
        unique.setdefault(fingerprint(item), item)
    remaining = list(unique.values())
    if len(remaining) < count:
        raise ValueError(
            f"only {len(remaining)} unique semantic fingerprints remain for {count} requested plans"
        )

    rng.shuffle(remaining)
    selected: list[dict[str, Any]] = []
    used_venues: set[str] = set()
    used_outfits: set[tuple[str, ...]] = set()
    field_counts = {field: Counter() for field in FINGERPRINT_FIELDS}
    pose_counts: Counter[str] = Counter()
    long_denim_count = 0
    long_trouser_count = 0

    while len(selected) < count:
        viable = []
        for item in remaining:
            if item["venue"] in used_venues:
                continue
            if outfit_fingerprint(item) in used_outfits:
                continue
            if selected and distance(item, selected[-1]) < 4:
                continue
            if has_forbidden_shoulder(item):
                continue
            if ambiguous_hosiery(item):
                continue
            if has_short_hosiery(item):
                continue
            if is_long_denim(item) and long_denim_count >= max(1, round(count / 100)):
                continue
            if is_long_trouser(item) and long_trouser_count >= max(1, round(count * 0.02)):
                continue
            viable.append(item)

        if not viable:
            raise RuntimeError(
                "candidate pool exhausted before satisfying venue, outfit, and adjacent-distance rules; "
                "add more independently constructed candidates"
            )

        ranked = sorted(
            viable,
            key=lambda item: score_candidate(item, selected, field_counts, pose_counts, rng),
            reverse=True,
        )
        top_band = ranked[: max(1, min(12, (len(ranked) + 9) // 10))]
        chosen = rng.choice(top_band)
        selected.append(chosen)
        remaining.remove(chosen)
        used_venues.add(chosen["venue"])
        used_outfits.add(outfit_fingerprint(chosen))
        for field in FINGERPRINT_FIELDS:
            field_counts[field][chosen[field]] += 1
        pose_counts[chosen["pose_family"]] += 1
        if is_long_denim(chosen):
            long_denim_count += 1
        if is_long_trouser(chosen):
            long_trouser_count += 1

    return selected


def assign_batch_flags(selected: list[dict[str, Any]], rng: random.Random) -> None:
    count = len(selected)
    direct = [True] * round(count * 0.60) + [False] * (count - round(count * 0.60))
    rng.shuffle(direct)
    for index, item in enumerate(selected):
        convention = "漫展" in item["venue"] or "同人展" in item["venue"]
        item["direct_gaze"] = direct[index]
        item["companion_camera"] = rng.random() < 0.20
        item["cos_mode"] = convention or rng.random() < 0.10
        item["aspect_ratio"] = rng.choices(RATIOS, weights=RATIO_WEIGHTS, k=1)[0]
        item["emotion"] = rng.choice(EMOTIONS)


def audit(selected: list[dict[str, Any]]) -> dict[str, Any]:
    distances = [distance(selected[index - 1], selected[index]) for index in range(1, len(selected))]
    return {
        "count": len(selected),
        "unique_fingerprints": len({fingerprint(item) for item in selected}),
        "unique_venues": len({item["venue"] for item in selected}),
        "unique_outfit_fingerprints": len({outfit_fingerprint(item) for item in selected}),
        "scene_domains": len({item["scene_domain"] for item in selected}),
        "spatial_archetypes": len({item["spatial_archetype"] for item in selected}),
        "activities": len({item["activity"] for item in selected}),
        "outfit_pairings": len(
            {(item["top_silhouette"], item["bottom_silhouette"]) for item in selected}
        ),
        "pose_families": dict(Counter(item["pose_family"] for item in selected)),
        "direct_gaze": sum(bool(item["direct_gaze"]) for item in selected),
        "companion_camera": sum(bool(item["companion_camera"]) for item in selected),
        "cos_mode": sum(bool(item["cos_mode"]) for item in selected),
        "aspect_ratios": dict(Counter(item["aspect_ratio"] for item in selected)),
        "emotions": dict(Counter(item["emotion"] for item in selected)),
        "minimum_adjacent_fingerprint_distance": min(distances) if distances else None,
        "forbidden_shoulder_structures": sum(has_forbidden_shoulder(item) for item in selected),
        "ambiguous_hosiery_forms": sum(ambiguous_hosiery(item) for item in selected),
        "short_hosiery": sum(has_short_hosiery(item) for item in selected),
        "long_denim": sum(is_long_denim(item) for item in selected),
        "all_long_trousers": sum(is_long_trouser(item) for item in selected),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON array of candidate plans")
    parser.add_argument("--output", required=True, type=Path, help="destination JSON file")
    parser.add_argument("--count", required=True, type=int, help="number of plans to select")
    parser.add_argument("--seed", help="optional reproducible seed; omit for system randomness")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("input root must be a JSON array")
        candidates = [normalized(item, index) for index, item in enumerate(raw, start=1)]
        rng = choose_rng(args.seed)
        selected = select(candidates, args.count, rng)
        assign_batch_flags(selected, rng)
        result = {"cards": selected, "audit": audit(selected)}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["audit"], ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
