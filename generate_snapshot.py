"""
Gera o arquivo PROJECT_SNAPSHOT.md com o conteúdo relevante do projeto.

Como usar:
    python generate_snapshot.py
Opcional:
    python generate_snapshot.py --output MeuSnapshot.md
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def collect_files(base: Path) -> list[Path]:
    """Retorna a lista de arquivos a incluir no snapshot."""
    fixed = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "app.py",
        "database.py",
        "models.py",
        "utils.py",
    ]

    dynamic = []
    dynamic += sorted((base / "services").glob("*.py"))
    dynamic += sorted((base / "pages").glob("*.py"))

    files: list[Path] = []
    for rel in fixed:
        path = base / rel
        if path.exists():
            files.append(path)
    files += [p for p in dynamic if p.exists()]
    return files


def build_snapshot(files: list[Path], output: Path) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = (
        f"Projeto: Sistema de Orçamentos - Snapshot completo gerado em {timestamp}\n\n"
        "Cada seção abaixo mostra o caminho do arquivo original seguido pelo conteúdo completo.\n"
    )

    parts = [header]
    for path in files:
        parts.append(f"\n----- {path.relative_to(output.parent)} -----\n")
        parts.append(path.read_text(encoding="utf-8"))

    output.write_text("".join(parts), encoding="utf-8")


def main() -> None:
    base = Path(__file__).parent

    parser = argparse.ArgumentParser(description="Gera PROJECT_SNAPSHOT.md consolidado.")
    parser.add_argument(
        "--output",
        "-o",
        default="PROJECT_SNAPSHOT.md",
        help="Caminho do arquivo de saída (padrão: PROJECT_SNAPSHOT.md)",
    )
    args = parser.parse_args()

    files = collect_files(base)
    if not files:
        raise SystemExit("Nenhum arquivo encontrado para snapshot.")

    output_path = (Path(args.output)).resolve()
    build_snapshot(files, output_path)
    print(f"Snapshot salvo em: {output_path}")


if __name__ == "__main__":
    main()
