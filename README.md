# Lumina OS

Sistema de inteligencia de negocio para Lumina. Su finalidad es transformar datos de Mercado Libre y de la operación interna en decisiones de inversión, validación de activos y aprendizaje acumulado.

## Estado

**Release:** v0.1.0 — Foundation  
**Alcance actual:** definición del dominio, estructura de trabajo y documentación base.  
**Canal de ventas inicial:** Mercado Libre.

## Principio rector

> Lumina identifica oportunidades, crea activos para probarlas, mide su desempeño y convierte los activos validados en negocios escalables.

Un activo no validado no se considera un fracaso si deja conocimiento útil para la siguiente decisión.

## Abrir el proyecto

1. Descomprimí este paquete en una carpeta de trabajo, por ejemplo `~/Documents/Lumina OS`.
2. Abrí la carpeta **Lumina OS** desde Visual Studio Code.
3. Revisá primero [`docs/business/DOC-101-dominio-del-negocio.md`](docs/business/DOC-101-dominio-del-negocio.md) y [`docs/roadmap/ROADMAP.md`](docs/roadmap/ROADMAP.md).

## Estructura

| Carpeta | Propósito |
|---|---|
| `docs/` | Decisiones, arquitectura, negocio y documentación técnica. |
| `database/` | Esquemas, migraciones y datos de prueba futuros. |
| `automation/` | Flujos n8n y scripts de automatización futuros. |
| `dashboard/` | Dashboard y componentes de visualización futuros. |
| `reports/` | Plantillas y reportes generados (no subir los confidenciales). |
| `data/` | Datos originales, procesados e históricos locales. |
| `src/` | Código de la aplicación y motores analíticos. |
| `assets/` | Recursos visuales y plantillas. |
| `logs/` | Registros de ejecución locales. |

## Reglas de seguridad

- Nunca subir credenciales, tokens ni archivos `.env` reales.
- No modificar los datos de `data/raw/`; son la fuente original.
- Las decisiones importantes deben quedar documentadas.
- La IA recomienda; las personas autorizan cambios de negocio.

## Próximo hito

Modelar la base de datos inicial y mapear los reportes reales de Mercado Libre al dominio de Lumina.
