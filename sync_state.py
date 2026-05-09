from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATE_MD = ROOT / "docs" / "STATE.md"
STATE_JSON = ROOT / "docs" / "state.json"
START = "<!-- STATE_JSON_START -->"
END = "<!-- STATE_JSON_END -->"


def extract_state_block(text: str) -> str:
    start_index = text.index(START) + len(START)
    end_index = text.index(END, start_index)
    block = text[start_index:end_index].strip()
    if block.startswith("```json"):
        block = block[len("```json") :].strip()
    if block.endswith("```"):
        block = block[:-3].strip()
    return block


def main() -> int:
    source = STATE_MD.read_text(encoding="utf-8")
    data = json.loads(extract_state_block(source))
    STATE_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
