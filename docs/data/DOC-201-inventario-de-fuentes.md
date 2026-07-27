# DOC-201 — Inventario de fuentes Mercado Libre

**Estado:** Revisado sobre el paquete histórico recibido el 2026-07-26.  
**Propósito:** documentar qué información existe antes de crear una importación automática.

## Resumen

Se recibieron **16 archivos**. Cubren ventas, publicaciones, stock, liquidaciones, publicidad, desempeño, reclamos y ventas con problemas. Es información suficiente para diseñar el MVP analítico.

## Fuentes identificadas

| Área | Archivo o grupo | Uso previsto | Observación |
|---|---|---|---|
| Ventas | 2 exportaciones `Ventas AR` | Órdenes, unidades, ingresos, cargos, envío, SKU y publicación. | Comparten 152 operaciones; no se deben sumar ambas sin deduplicación. |
| Publicaciones | `Publicaciones-...xlsx` | Item ID, SKU, título, variante, stock, precio y estado. | Es una foto del catálogo al momento de exportación. |
| Stock | `stock_general_full_...xlsx` | Stock y ventas de 30 días por publicación. | Es una foto de inventario; debe cargarse como snapshot fechado. |
| Liquidaciones | 2 CSV `settlement_v2` | Movimientos, comisiones, impuestos, monto neto y fecha de liberación. | Comparten 240 `SOURCE_ID`; conservar ambos originales y deduplicar al procesar. |
| Publicidad por campaña | 2 `report-campaigns` | Presupuesto, impresiones, clics, CPC, CTR, CVR, ACOS y ROAS. | Una exportación es mayo-junio y otra solo junio. |
| Publicidad por anuncio | 2 `report-pads` | Métricas por publicación/anuncio. | Misma lógica de períodos superpuestos. |
| Evolución del negocio | 2 `Reporte_evolucion_negocio` | Métricas mensuales, conversión, ventas, cancelaciones y devoluciones. | Una exportación incluye mayo-junio y la otra junio. |
| Desempeño de productos | 2 `Reporte_desempeño_producto` | Visitas, intención de compra y ventas brutas mensuales. | El archivo recibido contiene métricas agregadas, no detalle por SKU. |
| Reclamos | CSV de ventas con reclamos | Fecha, número, venta asociada, tipo y detalle. | Datos útiles para calidad y riesgo. |
| Ventas con problemas | `Ventas_con_problemas...xlsx` | Casos operativos pendientes. | Se revisará su layout al diseñar la importación. |

## Reglas de importación

1. Cada archivo original se conserva sin modificación en `data/raw/`.
2. Cada carga genera un registro con nombre, fecha de importación, período declarado y huella del archivo.
3. Las cargas superpuestas se deduplican usando identificadores externos y fechas; nunca por importes redondeados.
4. Los reportes de resumen son métricas de control: no reemplazan la tabla detallada de ventas.
5. Las exportaciones de stock y publicaciones son snapshots: se preserva la fecha de captura.

## Riesgos detectados

- Los reportes de ventas contienen datos personales de compradores. El modelo procesado guarda solo el identificador externo de la venta; no incorpora dirección, documento ni domicilio al MVP.
- Algunos reportes usan varias filas de título antes del encabezado real. La importación debe conocer el número de fila de encabezado por fuente.
- Los títulos de publicación no son claves estables. Las relaciones deben basarse en IDs de Mercado Libre, SKU o identificadores explícitamente validados.
