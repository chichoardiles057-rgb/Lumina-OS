-- Lumina OS v0.2.0 — esquema inicial para Supabase/PostgreSQL
-- Ejecutar únicamente en un proyecto Supabase de Lumina, después de revisión.

create extension if not exists pgcrypto;

create table if not exists source_imports (
  id uuid primary key default gen_random_uuid(),
  source_system text not null default 'mercado_libre',
  source_file_name text not null,
  source_file_sha256 text,
  report_type text not null,
  period_start date,
  period_end date,
  captured_at timestamptz,
  imported_at timestamptz not null default now(),
  row_count integer,
  import_status text not null default 'pending' check (import_status in ('pending','validated','imported','failed')),
  notes text
);

create table if not exists hypotheses (
  id uuid primary key default gen_random_uuid(),
  statement text not null,
  status text not null default 'active' check (status in ('draft','active','validated','refuted','archived')),
  created_at timestamptz not null default now(),
  closed_at timestamptz
);

create table if not exists assets (
  id uuid primary key default gen_random_uuid(),
  hypothesis_id uuid references hypotheses(id),
  name text not null,
  category text,
  status text not null default 'idea' check (status in ('idea','design','ready_to_validate','published','observing','validated','scaled','analysis','improvement','archived','replaced')),
  created_at timestamptz not null default now(),
  archived_at timestamptz
);

create table if not exists asset_versions (
  id uuid primary key default gen_random_uuid(),
  asset_id uuid not null references assets(id),
  version_number integer not null check (version_number > 0),
  sku text,
  development_cost_ars numeric(14,2),
  estimated_unit_cost_ars numeric(14,2),
  production_minutes numeric(12,2),
  change_summary text,
  created_at timestamptz not null default now(),
  unique (asset_id, version_number)
);

create table if not exists experiments (
  id uuid primary key default gen_random_uuid(),
  asset_version_id uuid not null references asset_versions(id),
  channel text not null default 'mercado_libre',
  started_on date not null,
  ends_on date not null,
  status text not null default 'active' check (status in ('planned','active','evaluating','validated','not_validated','closed')),
  sales_target numeric(14,2),
  margin_target_pct numeric(7,4),
  conversion_target_pct numeric(7,4),
  rating_target numeric(4,2),
  conclusion text,
  check (ends_on >= started_on)
);

create table if not exists marketplace_listings (
  id uuid primary key default gen_random_uuid(),
  marketplace text not null default 'mercado_libre',
  external_item_id text not null,
  asset_version_id uuid references asset_versions(id),
  sku text,
  title text,
  variation text,
  status text,
  first_seen_at timestamptz,
  last_seen_at timestamptz,
  unique (marketplace, external_item_id)
);

create table if not exists listing_snapshots (
  id uuid primary key default gen_random_uuid(),
  listing_id uuid not null references marketplace_listings(id),
  source_import_id uuid references source_imports(id),
  captured_at timestamptz not null,
  price_ars numeric(14,2),
  stock_flex numeric(14,2),
  stock_full numeric(14,2),
  shipping_method text,
  fee_per_sale numeric(14,2)
);

create table if not exists sales_orders (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  external_order_id text not null,
  marketplace_item_id text,
  sku text,
  sold_at timestamptz,
  sold_at_raw text,
  order_status text,
  units numeric(14,2),
  product_revenue_ars numeric(14,2),
  sale_fee_ars numeric(14,2),
  fixed_cost_ars numeric(14,2),
  installment_cost_ars numeric(14,2),
  shipping_revenue_ars numeric(14,2),
  shipping_cost_ars numeric(14,2),
  taxes_ars numeric(14,2),
  discounts_ars numeric(14,2),
  refunds_ars numeric(14,2),
  net_amount_ars numeric(14,2),
  is_ad_sale boolean,
  unique (external_order_id)
);

create table if not exists settlement_transactions (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  source_id text not null,
  transaction_type text not null,
  transaction_date timestamptz,
  settlement_date date,
  money_release_date date,
  payment_method_type text,
  transaction_amount_ars numeric(14,2),
  fee_amount_ars numeric(14,2),
  taxes_amount_ars numeric(14,2),
  real_amount_ars numeric(14,2),
  business_unit text,
  sub_unit text,
  unique (source_id, transaction_type, transaction_date, transaction_amount_ars, fee_amount_ars)
);

create table if not exists inventory_snapshots (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  captured_at timestamptz not null,
  marketplace_item_reference text,
  sku text,
  product_title text,
  sales_last_30d_units numeric(14,2),
  sales_last_30d_ars numeric(14,2),
  average_stock_last_30d numeric(14,2),
  quality_stock_units numeric(14,2)
);

create table if not exists ad_campaign_metrics (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  campaign_name text not null,
  campaign_status text,
  period_start date not null,
  period_end date not null,
  budget_ars numeric(14,2),
  target_roas numeric(14,4),
  impressions numeric(16,2),
  clicks numeric(16,2),
  cpc_ars numeric(14,2),
  ctr_pct numeric(9,4),
  conversion_pct numeric(9,4),
  acos_pct numeric(9,4),
  roas numeric(14,4)
);

create table if not exists ad_listing_metrics (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  marketplace_item_id text,
  campaign_name text,
  ad_title text,
  ad_status text,
  period_start date not null,
  period_end date not null,
  impressions numeric(16,2),
  clicks numeric(16,2),
  cpc_ars numeric(14,2),
  ctr_pct numeric(9,4),
  conversion_pct numeric(9,4),
  revenue_ars numeric(14,2),
  spend_ars numeric(14,2),
  acos_pct numeric(9,4),
  roas numeric(14,4)
);

create table if not exists claims (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  external_claim_id text not null,
  external_order_id text,
  claim_date date,
  claim_type text,
  claim_detail text,
  unique (external_claim_id)
);

create table if not exists business_metric_snapshots (
  id uuid primary key default gen_random_uuid(),
  source_import_id uuid references source_imports(id),
  metric_scope text not null check (metric_scope in ('business','product_performance','price_range','buyer_type')),
  period_label text,
  metric_name text not null,
  metric_value numeric(18,4),
  metric_value_text text
);

create table if not exists learnings (
  id uuid primary key default gen_random_uuid(),
  experiment_id uuid references experiments(id),
  learning_type text not null check (learning_type in ('observation','decision','result','lesson')),
  statement text not null,
  evidence text,
  recorded_at timestamptz not null default now()
);

create index if not exists idx_sales_orders_sold_at on sales_orders(sold_at);
create index if not exists idx_sales_orders_item on sales_orders(marketplace_item_id);
create index if not exists idx_settlement_source on settlement_transactions(source_id);
create index if not exists idx_ad_listing_item_period on ad_listing_metrics(marketplace_item_id, period_start, period_end);
