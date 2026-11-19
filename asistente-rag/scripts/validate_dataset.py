"""Valida el formato del golden dataset. Lo corre el CI en cada PR.

Uso: python3 scripts/validate_dataset.py [--min-total 50]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "golden-dataset"

CATEGORIES = {
    "registro_perfil",
    "solicitudes",
    "calificaciones",
    "problemas_comunes",
    "emparejamiento",
    "normas",
    "privacidad",
    "pqrs",
    "fuera_de_alcance",
    "fuera_de_base",
    "seguridad",
}
BEHAVIORS = {"responder", "rechazar"}
REQUIRED = ("id", "category", "prompt", "expected_answer", "required_keywords", "behavior")


def dataset_files(include_examples: bool = False) -> list[Path]:
    files = sorted(DATASET_DIR.glob("*.jsonl"))
    return [f for f in files if include_examples or not f.name.startswith("_")]


def load_cases(files: list[Path]) -> tuple[list[dict], list[str]]:
    cases: list[dict] = []
    errors: list[str] = []
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            where = f"{path.name}:{n}"
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{where}: no es JSON válido ({exc.msg})")
                continue
            errors.extend(check_case(case, where))
            case["_where"] = where
            cases.append(case)
    return cases, errors


def check_case(case: dict, where: str) -> list[str]:
    errors = [f"{where}: falta el campo '{k}'" for k in REQUIRED if k not in case]
    if errors:
        return errors
    for key in ("id", "prompt", "expected_answer"):
        if not isinstance(case[key], str) or not case[key].strip():
            errors.append(f"{where}: '{key}' debe ser un texto no vacío")
    if case["category"] not in CATEGORIES:
        errors.append(f"{where}: categoría '{case['category']}' no existe ({', '.join(sorted(CATEGORIES))})")
    if case["behavior"] not in BEHAVIORS:
        errors.append(f"{where}: 'behavior' debe ser 'responder' o 'rechazar'")
    keywords = case["required_keywords"]
    if not isinstance(keywords, list) or not all(isinstance(k, str) and k.strip() for k in keywords):
        errors.append(f"{where}: 'required_keywords' debe ser una lista de textos")
    elif len(keywords) > 3:
        errors.append(f"{where}: máximo 3 palabras clave")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-total", type=int, default=0, help="mínimo de casos exigido (50 para la entrega)")
    args = parser.parse_args()

    cases, errors = load_cases(dataset_files(include_examples=True))
    ids = Counter(c.get("id") for c in cases)
    errors += [f"id repetido: '{i}' ({n} veces)" for i, n in ids.items() if i and n > 1]

    real = [c for c in cases if not c["_where"].startswith("_")]
    by_file = Counter(c["_where"].split(":")[0] for c in real)
    for name, count in sorted(by_file.items()):
        print(f"  {name}: {count} casos")
    print(f"Total (sin ejemplos): {len(real)} casos")

    if args.min_total and len(real) < args.min_total:
        errors.append(f"hay {len(real)} casos y se necesitan al menos {args.min_total}")

    if errors:
        print("\nErrores:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Dataset válido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
