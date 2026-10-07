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
    "outfit_architecture",
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
    "outfit_architecture",
    "outfit_family",
    "top_silhouette",
    "bottom_silhouette",
    "material",
    "artistic_finish",
)

OUTFIT_FIELDS = (
    "outfit_architecture",
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

FORBIDDEN_SHOULDER_TERMS = ("单肩", "斜肩", "不对称肩", "单侧肩", "一字斜肩", "斜领", "单袖", "一边有袖")
HOSIERY_FORM_TERMS = ("中筒", "及膝", "过膝", "大腿", "吊带", "连裤袜", "裤袜")
SHORT_HOSIERY_TERMS = ("短袜", "短筒", "船袜", "踝袜", "ankle sock", "ankle socks", "no-show sock", "no-show socks")
LONG_DENIM_TERMS = ("牛仔长裤", "丹宁长裤", "微喇牛仔", "直筒牛仔长裤", "破洞牛仔长裤")
LONG_TROUSER_TERMS = ("长裤", "微喇裤", "直筒裤", "机能长裤", "西装长裤", "牛仔长裤", "丹宁长裤")

FORBIDDEN_GARMENT_TERMS = (
    "皮革", "仿皮", "pu皮", "PU皮", "墨绿色", "墨绿", "深绿色", "深绿",
    "焦糖色", "焦糖", "银色反光连体衣", "银色反光连体",
)
FORBIDDEN_WAIST_CUTOUT_TERMS = (
    "腰侧小面积镂空", "腰侧镂空", "侧腰镂空", "腹部镂空", "腰部镂空",
    "腰侧开口", "侧腰开口", "腹部开口", "腰部局部切口", "腰侧裁片", "侧腰裁片",
)

CROPPED_TWO_PIECE_TERMS = (
    "露腰两件套", "短上衣＋短裙", "短上衣+短裙", "短上衣＋短裤", "短上衣+短裤",
    "运动分体套装", "新中式两件套", "古风两件套", "新中式 / 古风两件套",
)



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


def candidate_wardrobe_text(candidate: dict[str, Any]) -> str:
    return " ".join(
        clean(candidate.get(field, ""))
        for field in (
            "outfit_family", "top_silhouette", "bottom_silhouette", "material",
            "hosiery", "color", "outfit_notes",
        )
    )


def has_forbidden_garment(candidate: dict[str, Any]) -> bool:
    text = candidate_wardrobe_text(candidate)
    return any(term.lower() in text.lower() for term in FORBIDDEN_GARMENT_TERMS)


def has_forbidden_waist_cutout(candidate: dict[str, Any]) -> bool:
    text = candidate_wardrobe_text(candidate)
    return any(term in text for term in FORBIDDEN_WAIST_CUTOUT_TERMS)


def architecture_target(count: int) -> int:
    if count >= 50:
        return 10
    if count >= 20:
        return 8
    if count >= 10:
        return 6
    if count >= 5:
        return 4
    return min(count, 3)


def is_cropped_two_piece(candidate: dict[str, Any]) -> bool:
    architecture = clean(candidate.get("outfit_architecture", ""))
    return any(term in architecture for term in CROPPED_TWO_PIECE_TERMS)

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

    target_architectures = architecture_target(count)
    eligible_architectures = {
        item["outfit_architecture"]
        for item in remaining
        if not has_forbidden_shoulder(item)
        and not has_forbidden_garment(item)
        and not has_forbidden_waist_cutout(item)
        and not has_short_hosiery(item)
        and not ambiguous_hosiery(item)
    }
    if len(eligible_architectures) < target_architectures:
        raise RuntimeError(
            f"candidate pool has only {len(eligible_architectures)} eligible macro outfit architectures; "
            f"need at least {target_architectures} for a batch of {count}"
        )

    rng.shuffle(remaining)
    selected: list[dict[str, Any]] = []
    used_venues: set[str] = set()
    used_outfits: set[tuple[str, ...]] = set()
    used_architectures: set[str] = set()
    architecture_counts: Counter[str] = Counter()
    cropped_two_piece_count = 0
    cropped_two_piece_limit = max(1, (count * 2 + 4) // 5)
    per_architecture_cap = max(2, (count + 3) // 4)
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
            if has_forbidden_garment(item):
                continue
            if has_forbidden_waist_cutout(item):
                continue
            if ambiguous_hosiery(item):
                continue
            if has_short_hosiery(item):
                continue
            if is_long_denim(item) and long_denim_count >= max(1, round(count / 100)):
                continue
            if is_long_trouser(item) and long_trouser_count >= max(1, round(count * 0.02)):
                continue
            architecture = item["outfit_architecture"]
            if architecture_counts[architecture] >= per_architecture_cap:
                continue
            if len(selected) >= 2 and selected[-1]["outfit_architecture"] == architecture and selected[-2]["outfit_architecture"] == architecture:
                continue
            if is_cropped_two_piece(item) and cropped_two_piece_count >= cropped_two_piece_limit:
                continue
            unseen_needed = max(0, target_architectures - len(used_architectures))
            remaining_slots = count - len(selected)
            if unseen_needed >= remaining_slots and architecture in used_architectures:
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
        used_architectures.add(chosen["outfit_architecture"])
        architecture_counts[chosen["outfit_architecture"]] += 1
        if is_cropped_two_piece(chosen):
            cropped_two_piece_count += 1
        for field in FINGERPRINT_FIELDS:
            field_counts[field][chosen[field]] += 1
        pose_counts[chosen["pose_family"]] += 1
        if is_long_denim(chosen):
            long_denim_count += 1
        if is_long_trouser(chosen):
            long_trouser_count += 1

    return selected


def is_static_standing(candidate: dict[str, Any]) -> bool:
    pose = clean(candidate.get("pose_family", ""))
    dynamic_tokens = ("行走", "走", "跑", "跳", "转身", "停步", "侧步", "漫步", "动态", "自拍", "镜前")
    standing_tokens = ("站姿", "站立", "站", "倚靠")
    return any(token in pose for token in standing_tokens) and not any(token in pose for token in dynamic_tokens)


def separated_direct_flags(count: int, rng: random.Random) -> list[bool]:
    direct_count = round(count * 0.80)
    false_count = count - direct_count
    flags = [True] * count
    if false_count <= 0:
        return flags

    candidates = list(range(count))
    rng.shuffle(candidates)
    chosen: list[int] = []
    for index in candidates:
        if all(abs(index - other) > 1 for other in chosen):
            chosen.append(index)
            if len(chosen) == false_count:
                break

    if len(chosen) < false_count:
        remaining = [index for index in range(count) if index not in chosen]
        rng.shuffle(remaining)
        chosen.extend(remaining[: false_count - len(chosen)])

    for index in chosen:
        flags[index] = False
    return flags


def assign_batch_flags(selected: list[dict[str, Any]], rng: random.Random) -> None:
    count = len(selected)
    direct = separated_direct_flags(count, rng)
    static_full_body_budget = max(0, int(count * 0.10))
    static_full_body_used = 0

    for index, item in enumerate(selected):
        convention = "漫展" in item["venue"] or "同人展" in item["venue"]
        item["direct_gaze"] = direct[index]
        item["companion_camera"] = rng.random() < 0.20
        item["cos_mode"] = convention or rng.random() < 0.10
        item["aspect_ratio"] = rng.choices(RATIOS, weights=RATIO_WEIGHTS, k=1)[0]
        item["emotion"] = rng.choice(EMOTIONS)

        if is_static_standing(item):
            if static_full_body_used < static_full_body_budget and rng.random() < 0.35:
                item["framing"] = "全身"
                static_full_body_used += 1
            else:
                item["framing"] = rng.choice(("半身", "膝上", "七分身"))
        else:
            item["framing"] = rng.choices(
                ("胸像", "半身", "膝上", "七分身", "全身"),
                weights=(10.0, 26.0, 28.0, 26.0, 10.0),
                k=1,
            )[0]


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
        "unique_outfit_architectures": len({item["outfit_architecture"] for item in selected}),
        "outfit_architectures": dict(Counter(item["outfit_architecture"] for item in selected)),
        "cropped_two_piece_architectures": sum(is_cropped_two_piece(item) for item in selected),
        "architecture_target": architecture_target(len(selected)),
        "pose_families": dict(Counter(item["pose_family"] for item in selected)),
        "direct_gaze": sum(bool(item["direct_gaze"]) for item in selected),
        "non_gaze_consecutive_pairs": sum(
            (not bool(selected[index - 1]["direct_gaze"])) and (not bool(selected[index]["direct_gaze"]))
            for index in range(1, len(selected))
        ),
        "static_standing": sum(is_static_standing(item) for item in selected),
        "static_standing_full_body": sum(
            is_static_standing(item) and item.get("framing") == "全身" for item in selected
        ),
        "pose_activity_pairs": len({(item["pose_family"], item["activity"]) for item in selected}),
        "framing": dict(Counter(item.get("framing", "") for item in selected)),
        "companion_camera": sum(bool(item["companion_camera"]) for item in selected),
        "cos_mode": sum(bool(item["cos_mode"]) for item in selected),
        "aspect_ratios": dict(Counter(item["aspect_ratio"] for item in selected)),
        "emotions": dict(Counter(item["emotion"] for item in selected)),
        "minimum_adjacent_fingerprint_distance": min(distances) if distances else None,
        "forbidden_shoulder_structures": sum(has_forbidden_shoulder(item) for item in selected),
        "forbidden_garments": sum(has_forbidden_garment(item) for item in selected),
        "forbidden_waist_cutouts": sum(has_forbidden_waist_cutout(item) for item in selected),
        "outfit_families": dict(Counter(item["outfit_family"] for item in selected)),
        "top_silhouettes": dict(Counter(item["top_silhouette"] for item in selected)),
        "bottom_silhouettes": dict(Counter(item["bottom_silhouette"] for item in selected)),
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
