# Lumina OS v0.3.3 — Fechas de reclamos

Esta actualización convierte automáticamente las fechas textuales de reclamos de Mercado Libre al formato que acepta la base de datos. También hace que el importador ignore líneas vacías duplicadas dentro de `.env` y reanude una carga parcial sin duplicar métricas.

Reemplazá únicamente:

```text
scripts/import_historical.py
```

Después registrá el ajuste:

```bash
git add scripts/import_historical.py INSTRUCCIONES_V0.3.3.md
git commit -m "v0.3.3 - Normalizar fechas de reclamos"
git push
```

Luego repetí la importación real con `--apply`.
