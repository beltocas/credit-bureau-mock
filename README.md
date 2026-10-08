# credit-bureau-mock

API **simulada** de scoring crediticio para el proyecto *Agente de Calificación de Leads*
(curso Agentes de IA, UTEC). Se sirve gratis desde GitHub (raw.githubusercontent.com),
con un archivo JSON por DNI en `scores/`.

> ⚠️ Todos los datos son ficticios. Los DNI `00000001`–`00000005` no corresponden a
> personas reales. No es un buró de crédito ni usa información de Equifax, Experian/Sentinel
> ni de la SBS.

## Endpoint

```
GET https://raw.githubusercontent.com/beltocas/credit-bureau-mock/main/scores/{dni}.json
```

Un DNI inexistente devuelve `404`. GitHub cachea los archivos unos minutos, así que un
cambio puede tardar en verse.

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

## `db.json`

Contiene los mismos perfiles en el formato de
[My JSON Server](https://my-json-server.typicode.com/) (`GET .../scores/{dni}`), que se
dejó como alternativa: en octubre de 2026 el servicio respondía `error code: 1016`.
Si cambias un perfil, actualiza `db.json` y el archivo en `scores/`.
