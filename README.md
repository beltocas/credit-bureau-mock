# credit-bureau-mock

API **simulada** de scoring crediticio para el proyecto *Agente de Calificación de Leads*
(curso Agentes de IA, UTEC). Se sirve gratis desde GitHub (raw.githubusercontent.com),
con un archivo JSON por DNI en `scores/`.

> ⚠️ Todos los datos son ficticios. Los DNI no corresponden a personas reales. No es un
> buró de crédito ni usa información de Equifax, Experian/Sentinel ni de la SBS.

## Endpoint

```
GET https://raw.githubusercontent.com/beltocas/credit-bureau-mock/main/scores/{dni}.json
```

Un DNI inexistente devuelve `404`. GitHub cachea los archivos unos minutos, así que un
cambio puede tardar en verse.

## Perfiles (1.005)

| DNI | Origen | Para qué |
|---|---|---|
| `00000001`–`00000005` | `profiles/curated.json` (escritos a mano) | Casos controlados para tests y demo, incluido "sin historial" |
| `10000001`–`10001000` | Muestra de 1.000 filas del dataset de Kaggle | Volumen y variedad |

Casos curados:

| DNI | score | risk_level | sbs_rating |
|---|---|---|---|
| 00000001 | 780 | bajo | Normal |
| 00000002 | 610 | medio | CPP |
| 00000003 | 420 | alto | Deficiente |
| 00000004 | — | sin_historial | — |
| 00000005 | 250 | muy_alto | Dudoso |

Ejemplo de perfil generado:

```json
{
  "id": "10000001",
  "score": 580,
  "risk_level": "muy_alto",
  "sbs_rating": "Deficiente",
  "total_debt_pen": 371362.5,
  "active_entities": 5,
  "updated_at": "2026-09-30",
  "source": "kaggle:lorenzozoppelletto/financial-risk-for-loan-approval",
  "source_row": 13
}
```

## Dataset de origen

[Financial Risk for Loan Approval](https://www.kaggle.com/datasets/lorenzozoppelletto/financial-risk-for-loan-approval)
(Kaggle, autor `lorenzozoppelletto`): 20.000 registros sintéticos con 36 columnas.

### Cómo se mapea cada campo

| Campo | Columna de Kaggle | Regla |
|---|---|---|
| `id` | — | DNI ficticio correlativo desde `10000001` |
| `score` | `CreditScore` | Tal cual (en el dataset va de 343 a 712) |
| `risk_level` | `RiskScore` | Cuartiles del dataset completo (mayor = más riesgo): `< 46` bajo · `< 52` medio · `< 56` alto · resto muy_alto |
| `sbs_rating` | `PreviousLoanDefaults`, `BankruptcyHistory` y `risk_level` | impago + quiebra → Pérdida · quiebra → Dudoso · impago → Deficiente · riesgo alto/muy_alto → CPP · resto → Normal |
| `total_debt_pen` | `TotalLiabilities` | USD × 3.75 (tipo de cambio fijo y referencial) |
| `active_entities` | `NumberOfOpenCreditLines` | Tal cual |
| `updated_at` | — | Fecha fija `2026-09-30`: `ApplicationDate` es sintética y llega hasta 2072 |
| `source_row` | — | Índice de la fila en `Loan.csv` (0 = primera fila de datos), para trazabilidad |

`sbs_rating` es una **aproximación** para dar coherencia al mock. No es la metodología
oficial de la SBS.

## Regenerar los perfiles

`raw/` no se sube al repo: cada quien descarga el CSV de Kaggle.

1. Descarga `Loan.csv` del enlace de arriba (requiere cuenta de Kaggle) y déjalo en `raw/Loan.csv`.
2. Ejecuta:

```bash
python3 build_profiles.py
```

El script verifica las columnas y luego genera `scores/`, `db.json` y la copia local del
agente en `../lead-agent-platform/data/mock/credit_bureau_db.json`. Usa una semilla fija:
mismo CSV produce los mismos perfiles. Opciones: `--sample-size 2000`, `--seed 7` y
`--local-copy ""` (para no escribir la copia local).

Para cambiar un caso curado, edita `profiles/curated.json` y vuelve a ejecutar el script.
No edites `scores/` a mano: se regenera.

## `db.json`

Contiene los mismos perfiles en el formato de
[My JSON Server](https://my-json-server.typicode.com/) (`GET .../scores/{dni}`), que se
dejó como alternativa: en octubre de 2026 el servicio respondía `error code: 1016`.
