"""Run labeled meeting-extraction evaluation against the configured Ollama model."""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def normalise_deadline(value: str) -> str:
    return re.sub(r"^(?:by|before|on|due(?: by)?)\s+", "", normalise(value))


def task_similarity(left: str, right: str) -> float:
    left_words = set(normalise(left).split())
    right_words = set(normalise(right).split())
    return len(left_words & right_words) / len(left_words | right_words) if left_words or right_words else 1.0


def items_match(expected: dict, actual: dict) -> bool:
    return (
        normalise(expected["assignee"]) == normalise(actual.assignee)
        and task_similarity(expected["task"], actual.task) >= 0.6
        and normalise_deadline(expected["deadline"]) == normalise_deadline(actual.deadline)
        and normalise(expected["priority"]) == normalise(actual.priority)
    )


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Ollama model tag, e.g. qwen2.5:3b")
    parser.add_argument("--dataset", type=Path, default=Path(__file__).with_name("meeting_extraction.json"))
    parser.add_argument("--limit", type=int, help="Evaluate only the first N cases (for smoke tests)")
    parser.add_argument("--details", action="store_true", help="Print predictions for failed cases")
    args = parser.parse_args()
    if args.model:
        os.environ["OLLAMA_MODEL"] = args.model

    from app.services.meeting_service import MeetingService

    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    if args.limit is not None:
        cases = cases[:args.limit]
    service = MeetingService()
    date_correct = department_correct = matched = expected_total = predicted_total = exact_cases = 0
    failures = []
    try:
        for case in cases:
            actual = await service.analyze_meeting(case["transcript"])
            expected = case["expected"]
            date_ok = normalise(actual.meeting_date) == normalise(expected["meeting_date"])
            department_ok = normalise(actual.department) == normalise(expected["department"])
            date_correct += date_ok
            department_correct += department_ok
            unmatched = list(actual.action_items)
            case_matches = 0
            for expected_item in expected["action_items"]:
                index = next((i for i, item in enumerate(unmatched) if items_match(expected_item, item)), None)
                if index is not None:
                    unmatched.pop(index)
                    case_matches += 1
            matched += case_matches
            expected_total += len(expected["action_items"])
            predicted_total += len(actual.action_items)
            if date_ok and department_ok and case_matches == len(expected["action_items"]) and not unmatched:
                exact_cases += 1
            else:
                failures.append(case["id"])
                if args.details:
                    print(json.dumps({"case": case["id"], "expected": expected, "actual": actual.model_dump()}, ensure_ascii=False))
    finally:
        await service.meeting_agent.close()

    precision = matched / predicted_total if predicted_total else 1.0
    recall = matched / expected_total if expected_total else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    metrics = {
        "cases": len(cases),
        "date_accuracy": round(date_correct / len(cases), 4),
        "department_accuracy": round(department_correct / len(cases), 4),
        "action_item_precision": round(precision, 4),
        "action_item_recall": round(recall, 4),
        "action_item_f1": round(f1, 4),
        "exact_case_accuracy": round(exact_cases / len(cases), 4),
        "failed_case_ids": failures,
    }
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
