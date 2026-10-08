# credit-bureau-mock

API **simulada** de scoring crediticio para el proyecto *Agente de Calificación de Leads*
(curso Agentes de IA, UTEC). Se sirve gratis con
[My JSON Server](https://my-json-server.typicode.com/) a partir de `db.json`.

> ⚠️ Todos los datos son ficticios. Los DNI `00000001`–`00000005` no corresponden a
> personas reales. No es un buró de crédito ni usa información de Equifax, Experian/Sentinel
> ni de la SBS.

## Endpoints

```
GET https://my-json-server.typicode.com/<usuario>/credit-bureau-mock/scores
GET https://my-json-server.typicode.com/<usuario>/credit-bureau-mock/scores/{dni}
```

Un DNI inexistente devuelve `404`.

## Perfiles

| DNI | score | risk_level | sbs_rating |
|---|---|---|---|
| 00000001 | 780 | bajo | Normal |
| 00000002 | 610 | medio | CPP |
| 00000003 | 420 | alto | Deficiente |
| 00000004 | — | sin_historial | — |
| 00000005 | 250 | muy_alto | Dudoso |

El `score` va de 0 a 999. `sbs_rating` usa las categorías de calificación del deudor
de la SBS (Normal, CPP, Deficiente, Dudoso, Pérdida).

## Limitaciones de My JSON Server

- Solo lectura: los POST/PUT/DELETE responden, pero no persisten.
- `db.json` debe estar en la raíz de un repositorio **público** y pesar menos de 10 KB.
