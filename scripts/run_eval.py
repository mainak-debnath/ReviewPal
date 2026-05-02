from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.models import ReviewComment
from src.core.processors import build_added_line_lookup, chunk_diffs
from src.core.validator import validate_comments


def main() -> None:
    benchmark_path = Path(__file__).resolve().parents[1] / "evals" / "review_benchmark.json"
    cases = json.loads(benchmark_path.read_text(encoding="utf-8"))

    passed = 0
    for case in cases:
        chunks = chunk_diffs(case["diff"])
        valid_line_lookup = build_added_line_lookup(chunks)

        simulated_comments = [
            ReviewComment(
                path=item["filename"],
                line=line,
                body=f"Benchmark comment for line {line}",
                confidence=0.9,
            )
            for item in case["diff"]
            for line in valid_line_lookup.get(item["filename"], set())
        ]

        valid = validate_comments(simulated_comments, chunks, min_confidence=0.65)
        returned_lines = sorted(comment.line for comment in valid)
        forbidden_lines = set(case["forbidden_comment_lines"])

        is_valid = (
            all(line not in forbidden_lines for line in returned_lines)
            and set(case["expected_comment_lines"]).issubset(returned_lines)
        )

        status = "PASS" if is_valid else "FAIL"
        print(f"{status} {case['name']}: {returned_lines}")
        passed += int(is_valid)

    print(f"{passed}/{len(cases)} benchmark cases passed")


if __name__ == "__main__":
    main()
