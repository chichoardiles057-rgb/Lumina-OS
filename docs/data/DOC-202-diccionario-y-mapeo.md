# DOC-202 — Diccionario y mapeo inicial

**Estado:** Base para importación histórica.  
**Regla:** un campo de una exportación no se convierte en clave relacional hasta que se valide su consistencia entre fuentes.

## Claves candidatas

| Fuente | Campo | Uso | Confiabilidad inicial |
|---|---|---|---|
| Ventas | `# de venta` | Identificador externo de una orden. | Alta |
| Ventas | `# de publicación` | Identificador de publicación asociado a la venta. | Alta, pendiente de normalización de formato. |
| Ventas / publicaciones | `SKU` | Vínculo con activo o variante propia. | Media: puede estar vacío. |
| Publicaciones | `ITEM_ID` | Identificador Mercado Libre de la publicación. | Alta |
| Stock | `# Publicación` | Referencia de inventario por publicación. | Media: el formato debe validarse contra `ITEM_ID`. |
| Liquidaciones | `SOURCE_ID` | Movimiento fuente de liquidación. | Alta dentro de liquidaciones; relación con venta pendiente de validar. |
| Reclamos | `# de la venta` | Vínculo del reclamo con una orden. | Alta |

## Mapeo de ventas

| Campo de origen | Campo destino | Nota |
|---|---|---|
| `# de venta` | `sales_orders.external_order_id` | Único por orden tras deduplicación. |
| `Fecha de venta` | `sales_orders.sold_at_raw` / `sold_at` | Conservar texto original y fecha normalizada. |
| `Estado` | `sales_orders.order_status` | Ej.: Entregado. |
| `Unidades` | `sales_orders.units` | Hay columnas repetidas de unidades; se usará la correspondiente a la línea de venta, documentada durante la carga. |
| `Ingresos por productos (ARS)` | `sales_orders.product_revenue_ars` | Ingreso bruto de productos. |
| `Total (ARS)` | `sales_orders.net_amount_ars` | Neto informado por el reporte, no margen final interno. |
| `Cargo por venta`, `Costo fijo`, `Costo por ofrecer cuotas`, `Impuestos` | `sales_orders.*_ars` | Componentes de costos de plataforma. |
| `Venta por publicidad` | `sales_orders.is_ad_sale` | Atribución informada por Mercado Libre. |
| `SKU` | `sales_orders.sku` | Puede permitir vincular una versión de activo. |
| `# de publicación` | `sales_orders.marketplace_item_id` | Vínculo hacia publicación. |

## Mapeo de publicaciones, stock y publicidad

| Fuente | Campos relevantes | Tabla destino |
|---|---|---|
| Publicaciones | `ITEM_ID`, `SKU`, `TITLE`, `VARIATIONS`, `PRICE`, `STATUS`, stocks | `marketplace_listings` + `listing_snapshots` |
| Stock | código, SKU, publicación, producto, ventas 30 días, stock promedio, unidades buena calidad | `inventory_snapshots` |
| Campañas | nombre, estado, presupuesto, objetivo ROAS, período y métricas | `ad_campaign_metrics` |
| Anuncios | campaña, publicación, estado, impresiones, clics, CPC, CTR, CVR, ingresos, inversión, ACOS, ROAS | `ad_listing_metrics` |

## Métricas agregadas

Los reportes de evolución y desempeño se cargan en `business_metric_snapshots`. Sirven para reconciliar el detalle de ventas y observar visitas/conversión cuando no existe detalle por publicación.

## Datos que Lumina debe aportar

Para calcular margen real y validación de un activo faltan datos internos: costo unitario, costo de desarrollo, tiempo de producción, categoría, responsable, hipótesis y fechas del experimento. Estos datos no deben inferirse desde Mercado Libre.
