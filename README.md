# Lumina OS

Sistema de inteligencia de negocio para Lumina.

## Estado

**Release:** v0.2.0 — Modelo de datos inicial  
**Canal integrado en diseño:** Mercado Libre  
**Datos revisados:** 16 exportaciones históricas de ventas, liquidaciones, publicaciones, stock, publicidad, desempeño y reclamos.

## Qué resuelve esta versión

Esta versión convierte los reportes de Mercado Libre en un diseño de base de datos preparado para cargar históricos sin mezclar archivos ni duplicar operaciones. Aún no conecta la API ni altera datos reales.

## Documentos principales

- [`docs/data/DOC-201-inventario-de-fuentes.md`](docs/data/DOC-201-inventario-de-fuentes.md)
- [`docs/data/DOC-202-diccionario-y-mapeo.md`](docs/data/DOC-202-diccionario-y-mapeo.md)
- [`docs/database/DOC-203-modelo-fisico-inicial.md`](docs/database/DOC-203-modelo-fisico-inicial.md)
- [`database/schema/001_lumina_core.sql`](database/schema/001_lumina_core.sql)

## Regla de protección de datos

Los archivos originales siguen en `data/raw/` y no se suben a GitHub. Los datos personales de compradores no se usan para el MVP salvo que una decisión de negocio lo justifique expresamente.
