#!/usr/bin/env python3
"""Importador histórico controlado para Lumina OS.

Por defecto corre en modo seguro (--dry-run): lee un ZIP de Mercado Libre,
resume las filas detectadas y no se conecta ni escribe en Supabase.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pandas as pd


def clean(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return None if text in ("", "-", "nan", "None") else text


def numeric(value):
    if pd.isna(value) or str(value).strip() in ("", "-"):
        return None
    try:
        return float(str(value).replace(".", "").replace(",", ".")) if isinstance(value, str) and "," in value else float(value)
    except (TypeError, ValueError):
        return None


def flag(value):
    if pd.isna(value):
        return None
    return str(value).strip().lower() in ("sí", "si", "yes", "true", "1")


def frame(path, **kwargs):
    return pd.read_excel(path, **kwargs)


def sales_rows(root):
    records = []
    for path in sorted(root.glob("*Ventas_AR*.xlsx")):
        df = frame(path, sheet_name="Ventas AR", skiprows=5)
        df = df[df["# de venta"].notna()]
        for _, row in df.iterrows():
            order_id = clean(row.get("# de venta"))
            if not order_id:
                continue
            records.append({
                "external_order_id": order_id,
                "marketplace_item_id": clean(row.get("# de publicación")),
                "sku": clean(row.get("SKU")),
                "sold_at_raw": clean(row.get("Fecha de venta")),
                "order_status": clean(row.get("Estado")),
                "units": numeric(row.get("Unidades")),
                "product_revenue_ars": numeric(row.get("Ingresos por productos (ARS)")),
                "sale_fee_ars": numeric(row.get("Cargo por venta")),
                "fixed_cost_ars": numeric(row.get("Costo fijo")),
                "installment_cost_ars": numeric(row.get("Costo por ofrecer cuotas")),
                "shipping_revenue_ars": numeric(row.get("Ingresos por envío (ARS)")),
                "shipping_cost_ars": numeric(row.get("Costos de envío (ARS)")),
                "taxes_ars": numeric(row.get("Impuestos")),
                "discounts_ars": numeric(row.get("Descuentos y bonificaciones")),
                "refunds_ars": numeric(row.get("Anulaciones y reembolsos (ARS)")),
                "net_amount_ars": numeric(row.get("Total (ARS)")),
                "is_ad_sale": flag(row.get("Venta por publicidad")),
            })
    # Conserva la fila más completa si la misma venta aparece en dos exportaciones.
    unique = {}
    for item in records:
        score = sum(v is not None for v in item.values())
        old = unique.get(item["external_order_id"])
        if old is None or score > sum(v is not None for v in old.values()):
            unique[item["external_order_id"]] = item
    return records, list(unique.values())


def listing_rows(root):
    path = next(iter(root.glob("Publicaciones-*.xlsx")), None)
    if not path:
        return []
    df = frame(path, sheet_name="Publicaciones")
    df = df[df["ITEM_ID"].astype(str).str.startswith("ML", na=False)]
    return [{
        "marketplace": "mercado_libre",
        "external_item_id": clean(r.get("ITEM_ID")),
        "sku": clean(r.get("SKU")),
        "title": clean(r.get("TITLE")),
        "variation": clean(r.get("VARIATIONS")),
        "status": clean(r.get("STATUS")),
    } for _, r in df.iterrows()]


def settlement_rows(root):
    records = []
    for path in sorted(root.glob("settlement*.csv")):
        df = pd.read_csv(path, sep=";")
        for _, r in df.iterrows():
            records.append({
                "source_id": clean(r.get("SOURCE_ID")),
                "transaction_type": clean(r.get("TRANSACTION_TYPE")),
                "transaction_date": clean(r.get("TRANSACTION_DATE")),
                "settlement_date": clean(r.get("SETTLEMENT_DATE")),
                "money_release_date": clean(r.get("MONEY_RELEASE_DATE")),
                "payment_method_type": clean(r.get("PAYMENT_METHOD_TYPE")),
                "transaction_amount_ars": numeric(r.get("TRANSACTION_AMOUNT")),
                "fee_amount_ars": numeric(r.get("FEE_AMOUNT")),
                "taxes_amount_ars": numeric(r.get("TAXES_AMOUNT")),
                "real_amount_ars": numeric(r.get("REAL_AMOUNT")),
                "business_unit": clean(r.get("BUSINESS_UNIT")),
                "sub_unit": clean(r.get("SUB_UNIT")),
            })
    unique = {}
    for item in records:
        key = (item["source_id"], item["transaction_type"], item["transaction_date"], item["transaction_amount_ars"], item["fee_amount_ars"])
        unique[key] = item
    return records, list(unique.values())


def campaign_rows(root):
    records = []
    for path in sorted(root.glob("report-campaigns*.xlsx")):
        df = frame(path, sheet_name="Reporte por campañas", skiprows=1)
        df = df[df["Nombre de campaña"].notna()]
        for _, r in df.iterrows():
            records.append({
                "campaign_name": clean(r.get("Nombre de campaña")), "campaign_status": clean(r.get("Estado")),
                "period_start": clean(r.get("Desde")), "period_end": clean(r.get("Hasta")),
                "budget_ars": numeric(r.get("Presupuesto")), "target_roas": numeric(r.get("ROAS Objetivo")),
                "impressions": numeric(r.get("Impresiones")), "clicks": numeric(r.get("Clics")),
                "cpc_ars": numeric(r.get("CPC\n(Costo por clic)")), "ctr_pct": numeric(r.get("CTR\n(Click through rate)")),
                "conversion_pct": numeric(r.get("CVR\n(Conversion rate)")), "acos_pct": numeric(r.get("ACOS\n(Inversión / Ingresos)")),
                "roas": numeric(r.get("ROAS\n(Ingresos / Inversión)")),
            })
    return records


def ad_listing_rows(root):
    records = []
    for path in sorted(root.glob("report-pads*.xlsx")):
        df = frame(path, sheet_name="Reporte por Anuncios", skiprows=1)
        df = df[df["Número de \npublicación"].notna()]
        for _, r in df.iterrows():
            records.append({
                "marketplace_item_id": clean(r.get("Número de \npublicación")), "campaign_name": clean(r.get("Campaña")),
                "ad_title": clean(r.get("Título de anuncio")), "ad_status": clean(r.get("Estado")),
                "period_start": clean(r.get("Desde")), "period_end": clean(r.get("Hasta")),
                "impressions": numeric(r.get("Impresiones")), "clicks": numeric(r.get("Clics")),
                "cpc_ars": numeric(r.get("CPC \n(Costo por clic)")), "ctr_pct": numeric(r.get("CTR\n(Click Through Rate)")),
                "conversion_pct": numeric(r.get("CVR\n(Convertion rate)")), "revenue_ars": numeric(r.get("Ingresos\n(Moneda Local)")),
                "spend_ars": numeric(r.get("Inversión\n(Moneda Local)")), "acos_pct": numeric(r.get("ACOS\n(Inversión / Ingresos)")),
                "roas": numeric(r.get("ROAS\n(Ingresos / Inversión)")),
            })
    return records


def claim_rows(root):
    path = next(iter(root.glob("Reporte_de_ventas_con_reclamos*.csv")), None)
    if not path:
        return []
    df = pd.read_csv(path)
    return [{"external_claim_id": clean(r.get("Número de reclamo")), "external_order_id": clean(r.get("# de la venta")),
             "claim_date": clean(r.get("Fecha del reclamo")), "claim_type": clean(r.get("Tipo de reclamo")),
             "claim_detail": clean(r.get("Detalle del reclamo"))} for _, r in df.iterrows() if clean(r.get("Número de reclamo"))]


def env_value(name):
    value = os.getenv(name)
    if value:
        return value
    env = Path(__file__).resolve().parents[1] / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip("\"'")
    return None


def request(url, key, table, rows, conflict=None):
    if not rows:
        return
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    if conflict:
        endpoint += "?on_conflict=" + conflict
    headers = api_headers(key, "resolution=merge-duplicates,return=minimal")
    for start in range(0, len(rows), 250):
        http_json("POST", endpoint, headers, rows[start:start + 250])


def http_json(method, url, headers, payload):
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else []
    except HTTPError as error:
        body = error.read().decode("utf-8")
        raise RuntimeError(f"Supabase: {error.code} {body}") from error


def api_headers(key, prefer=None):
    headers = {"apikey": key, "Content-Type": "application/json"}
    # Las claves nuevas sb_secret no son JWT y no se envían como Bearer.
    if not key.startswith("sb_secret_"):
        headers["Authorization"] = f"Bearer {key}"
    if prefer:
        headers["Prefer"] = prefer
    return headers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, help="ZIP original descargado de Mercado Libre")
    parser.add_argument("--apply", action="store_true", help="Escribe en Supabase. Sin este indicador solo analiza.")
    args = parser.parse_args()
    zip_path = Path(args.zip).expanduser().resolve()
    if not zip_path.exists():
        sys.exit(f"No existe el ZIP: {zip_path}")
    with tempfile.TemporaryDirectory(prefix="lumina_import_") as temp:
        root = Path(temp)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(root)
        sales_all, sales = sales_rows(root)
        settlements_all, settlements = settlement_rows(root)
        payloads = {"marketplace_listings": listing_rows(root), "sales_orders": sales, "settlement_transactions": settlements,
                    "ad_campaign_metrics": campaign_rows(root), "ad_listing_metrics": ad_listing_rows(root), "claims": claim_rows(root)}
        summary = {name: len(rows) for name, rows in payloads.items()}
        summary.update({"sales_rows_detected": len(sales_all), "sales_duplicates_removed": len(sales_all) - len(sales),
                        "settlement_rows_detected": len(settlements_all), "settlement_duplicates_removed": len(settlements_all) - len(settlements)})
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        if not args.apply:
            print("\nModo seguro: no se escribió ningún dato. Usá --apply solo después de configurar .env.")
            return
        url = env_value("SUPABASE_URL")
        key = env_value("SUPABASE_SECRET_KEY") or env_value("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            sys.exit("Faltan SUPABASE_URL y SUPABASE_SECRET_KEY (o la clave legacy SUPABASE_SERVICE_ROLE_KEY) en .env. Nunca las compartas por chat ni las subas a GitHub.")
        checksum = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        import_row = {"source_file_name": zip_path.name, "source_file_sha256": checksum, "report_type": "historical_marketplace_zip", "captured_at": datetime.now(timezone.utc).isoformat(), "row_count": sum(summary[n] for n in payloads), "import_status": "validated"}
        endpoint = f"{url.rstrip('/')}/rest/v1/source_imports"
        headers = api_headers(key, "return=representation")
        import_id = http_json("POST", endpoint, headers, import_row)[0]["id"]
        # marketplace_listings es el catálogo actual y no guarda una referencia
        # directa al archivo; las tablas de hechos sí conservan su trazabilidad.
        for table, rows in payloads.items():
            if table == "marketplace_listings":
                continue
            for row in rows:
                row["source_import_id"] = import_id
        request(url, key, "marketplace_listings", payloads["marketplace_listings"], "marketplace,external_item_id")
        request(url, key, "sales_orders", payloads["sales_orders"], "external_order_id")
        request(url, key, "settlement_transactions", payloads["settlement_transactions"], "source_id,transaction_type,transaction_date,transaction_amount_ars,fee_amount_ars")
        request(url, key, "ad_campaign_metrics", payloads["ad_campaign_metrics"])
        request(url, key, "ad_listing_metrics", payloads["ad_listing_metrics"])
        request(url, key, "claims", payloads["claims"], "external_claim_id")
        http_json("PATCH", f"{url.rstrip('/')}/rest/v1/source_imports?id=eq.{import_id}", api_headers(key), {"import_status": "imported"})
        print("Importación completada.")


if __name__ == "__main__":
    main()
