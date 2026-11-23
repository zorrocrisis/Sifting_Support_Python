"""Small output helpers shared by the pilot scripts."""

import csv
import json
import math


def _clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_clean(v) for v in o]
    if hasattr(o, "item"):          # numpy scalars
        return _clean(o.item())
    return o


def write_json(path, obj):
    path.write_text(json.dumps(_clean(obj), indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    fieldnames = fieldnames or (list(rows[0].keys()) if rows else [])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def md_table(header, rows):
    def cell(v):
        if isinstance(v, float):
            return "–" if math.isnan(v) else f"{v:.3f}"
        return str(v).replace("|", "/").replace("\n", " ")
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def short(text, n=90):
    return text if len(text) <= n else text[: n - 1] + "…"
