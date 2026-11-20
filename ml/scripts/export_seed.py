"""Exporta los perfiles del dataset sintético al seed del backend (IA-06).

Escribe RedNexus-Backend/prisma/data/profiles.ts con los 50 ayudantes de ml/data/profiles.json más
la cuenta "Estudiante Demo" (sin habilidades, solo pide ayuda). Así la demo y los experimentos usan
los mismos perfiles. Requiere que RedNexus-Backend esté en la misma carpeta que RedNexus-Platform.

Uso (desde ml/): python scripts/export_seed.py
"""

import json
from pathlib import Path

ML = Path(__file__).resolve().parents[1]
BACKEND = ML.parents[1] / "RedNexus-Backend"
TARGET = BACKEND / "prisma" / "data" / "profiles.ts"


def ts_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> None:
    profiles = json.loads((ML / "data" / "profiles.json").read_text(encoding="utf-8"))
    lines = [
        "// Perfiles ficticios para la demo (Ley 1581): ningún dato es de una persona real.",
        "// Generado por RedNexus-Platform/ml/scripts/export_seed.py desde ml/data/profiles.json (IA-06).",
        "// No editar a mano: cambia el dataset y vuelve a correr el script.",
        "",
        "export interface SeedProfile {",
        "  email: string;",
        "  name: string;",
        "  bio: string | null;",
        "  tags: string[];",
        "}",
        "",
        "export const profiles: SeedProfile[] = [",
    ]
    for p in profiles:
        tags = ", ".join(ts_string(t) for t in p["tags"])
        lines += [
            "  {",
            f"    email: {ts_string(p['email'])},",
            f"    name: {ts_string(p['name'])},",
            f"    bio: {ts_string(p['bio'])},",
            f"    tags: [{tags}],",
            "  },",
        ]
    lines += [
        "  // sin habilidades: solo pide ayuda",
        "  {",
        "    email: 'estudiante.demo@rednexus.dev',",
        "    name: 'Estudiante Demo',",
        "    bio: null,",
        "    tags: [],",
        "  },",
        "];",
        "",
    ]
    TARGET.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(profiles) + 1} perfiles escritos en {TARGET}")


if __name__ == "__main__":
    main()
