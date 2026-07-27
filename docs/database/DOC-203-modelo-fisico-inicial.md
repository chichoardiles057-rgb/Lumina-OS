# DOC-203 — Modelo físico inicial

**Motor objetivo:** Supabase / PostgreSQL.  
**Estado:** listo para revisión antes de ejecutar.

## Modelo

```mermaid
erDiagram
  HYPOTHESES ||--o{ ASSETS : inspira
  ASSETS ||--o{ ASSET_VERSIONS : evoluciona
  ASSET_VERSIONS ||--o{ EXPERIMENTS : se_prueba_en
  ASSET_VERSIONS ||--o{ MARKETPLACE_LISTINGS : se_publica_como
  EXPERIMENTS ||--o{ LEARNINGS : genera
  MARKETPLACE_LISTINGS ||--o{ LISTING_SNAPSHOTS : registra
  MARKETPLACE_LISTINGS ||--o{ SALES_ORDERS : participa_en
  MARKETPLACE_LISTINGS ||--o{ INVENTORY_SNAPSHOTS : tiene
  MARKETPLACE_LISTINGS ||--o{ AD_LISTING_METRICS : recibe
  SALES_ORDERS ||--o{ CLAIMS : puede_tener
  SOURCE_IMPORTS ||--o{ SALES_ORDERS : proviene_de
  SOURCE_IMPORTS ||--o{ SETTLEMENT_TRANSACTIONS : proviene_de
```

## Decisiones

- `assets` y `asset_versions` representan la realidad de Lumina; no se crean desde una publicación automáticamente.
- `marketplace_listings` representa Mercado Libre y puede estar vinculado a una versión del activo cuando Lumina valide el SKU o la relación manualmente.
- Se conservan snapshots para publicaciones, stock, publicidad y métricas agregadas.
- `source_imports` permite rastrear cada dato al archivo original sin guardar datos personales en las tablas analíticas.
- Los valores monetarios se guardan como `numeric`, nunca como texto formateado.

## No ejecutar todavía si

- No se creó el proyecto Supabase.
- No se validó qué fila contiene el encabezado real de cada exportación en el proceso de importación.
- No se definió quién puede operar credenciales y cargas productivas.
