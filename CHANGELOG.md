# Changelog

Este proyecto sigue versionado semántico: `MAYOR.MENOR.PARCHE`.

## [0.2.0] — Modelo de datos inicial

### Agregado

- Inventario de las 16 exportaciones reales recibidas de Mercado Libre.
- Reglas de importación y deduplicación para archivos superpuestos.
- Diccionario de datos inicial y mapeo de fuentes hacia el dominio Lumina.
- Modelo físico inicial y esquema SQL compatible con Supabase/PostgreSQL.
- Política de minimización de datos personales de compradores.

### Pendiente

- Validar el esquema con una importación histórica controlada.
- Configurar Supabase y ejecutar la migración SQL.
- Definir umbrales por categoría para la validación de activos.

## [0.1.0] — Foundation

- Estructura inicial del proyecto, dominio del negocio, arquitectura conceptual y roadmap.
