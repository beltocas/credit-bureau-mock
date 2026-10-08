"""
Genera los perfiles de la API simulada de scoring crediticio.

Fuentes:
  - profiles/curated.json : 5 casos controlados (DNI 00000001-00000005)
                            que usan los tests y la demo.
  - raw/Loan.csv          : Kaggle "Financial Risk for Loan Approval"
                            (lorenzozoppelletto), 20.000 registros sinteticos.

Salidas:
  - scores/{dni}.json     : un archivo por DNI (lo sirve GitHub raw).
  - db.json               : todos los perfiles (formato My JSON Server).
  - --local-copy          : copia para el mock local del agente.

Uso:
  python3 build_profiles.py
  python3 build_profiles.py --sample-size 2000 --local-copy ""
"""

import argparse
import csv
import json
import random
import statistics
from pathlib import Path


ROOT = Path(__file__).parent

RAW_CSV = ROOT / "raw" / "Loan.csv"
CURATED_JSON = ROOT / "profiles" / "curated.json"
SCORES_DIR = ROOT / "scores"
DB_JSON = ROOT / "db.json"

DEFAULT_LOCAL_COPY = (
    ROOT.parent
    / "lead-agent-platform"
    / "data"
    / "mock"
    / "credit_bureau_db.json"
)

SOURCE = "kaggle:lorenzozoppelletto/financial-risk-for-loan-approval"

# Los DNI de Kaggle empiezan aqui para no chocar con los curados.
FIRST_GENERATED_ID = 10_000_001

# TotalLiabilities viene en USD. Tipo de cambio fijo y referencial.
USD_TO_PEN = 3.75

# ApplicationDate del dataset llega hasta 2072 (sintetico),
# asi que se usa una fecha de corte fija.
UPDATED_AT = "2026-09-30"

REQUIRED_COLUMNS = {
    "CreditScore",
    "RiskScore",
    "TotalLiabilities",
    "NumberOfOpenCreditLines",
    "PreviousLoanDefaults",
    "BankruptcyHistory",
}


def risk_cutoffs(rows: list[dict]) -> list[float]:
    """Cuartiles de RiskScore (mayor = mas riesgo)."""

    return statistics.quantiles(
        [float(row["RiskScore"]) for row in rows],
        n=4,
    )


def risk_level(
    risk_score: float,
    cutoffs: list[float],
) -> str:
    low, mid, high = cutoffs

    if risk_score < low:
        return "bajo"

    if risk_score < mid:
        return "medio"

    if risk_score < high:
        return "alto"

    return "muy_alto"


def sbs_rating(
    *,
    defaults: bool,
    bankruptcy: bool,
    level: str,
) -> str:
    """
    Aproximacion a la calificacion del deudor de la SBS.

    No es la metodologia oficial: solo da coherencia al mock.
    """

    if defaults and bankruptcy:
        return "Pérdida"

    if bankruptcy:
        return "Dudoso"

    if defaults:
        return "Deficiente"

    if level in ("alto", "muy_alto"):
        return "CPP"

    return "Normal"


def to_profile(
    row: dict,
    *,
    document_id: str,
    source_row: int,
    cutoffs: list[float],
) -> dict:
    level = risk_level(
        float(row["RiskScore"]),
        cutoffs,
    )

    return {
        "id": document_id,
        "score": int(float(row["CreditScore"])),
        "risk_level": level,
        "sbs_rating": sbs_rating(
            defaults=row["PreviousLoanDefaults"] == "1",
            bankruptcy=row["BankruptcyHistory"] == "1",
            level=level,
        ),
        "total_debt_pen": round(
            float(row["TotalLiabilities"]) * USD_TO_PEN,
            2,
        ),
        "active_entities": int(
            float(row["NumberOfOpenCreditLines"])
        ),
        "updated_at": UPDATED_AT,
        "source": SOURCE,
        "source_row": source_row,
    }


def load_rows() -> list[dict]:
    if not RAW_CSV.exists():
        raise SystemExit(
            f"No existe {RAW_CSV}. Descarga Loan.csv de Kaggle "
            "y dejalo en raw/."
        )

    with RAW_CSV.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)

        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])

        if missing:
            raise SystemExit(
                f"Faltan columnas en Loan.csv: {sorted(missing)}"
            )

        return list(reader)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--sample-size", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--local-copy",
        default=str(DEFAULT_LOCAL_COPY),
        help='Ruta del mock local del agente ("" para omitir).',
    )

    args = parser.parse_args()

    rows = load_rows()
    cutoffs = risk_cutoffs(rows)

    # Muestra reproducible: misma semilla = mismos perfiles.
    sampled_rows = sorted(
        random.Random(args.seed).sample(
            range(len(rows)),
            args.sample_size,
        )
    )

    generated = [
        to_profile(
            rows[source_row],
            document_id=str(FIRST_GENERATED_ID + offset),
            source_row=source_row,
            cutoffs=cutoffs,
        )
        for offset, source_row in enumerate(sampled_rows)
    ]

    with CURATED_JSON.open(encoding="utf-8") as file:
        curated = json.load(file)

    profiles = curated + generated

    # Regenera scores/ desde cero para no dejar archivos huerfanos.
    for old_file in SCORES_DIR.glob("*.json"):
        old_file.unlink()

    for profile in profiles:
        write_json(SCORES_DIR / f"{profile['id']}.json", profile)

    db = {"scores": profiles}

    write_json(DB_JSON, db)

    if args.local_copy:
        write_json(Path(args.local_copy), db)

    print(
        f"{len(profiles)} perfiles "
        f"({len(curated)} curados + {len(generated)} de Kaggle)"
    )
    print(
        "Cortes de RiskScore (bajo|medio|alto|muy_alto): "
        + " | ".join(f"{cut:.1f}" for cut in cutoffs)
    )

    for level in ("bajo", "medio", "alto", "muy_alto"):
        count = sum(1 for p in generated if p["risk_level"] == level)
        print(f"  {level}: {count}")

    if args.local_copy:
        print(f"Copia local: {args.local_copy}")


if __name__ == "__main__":
    main()
