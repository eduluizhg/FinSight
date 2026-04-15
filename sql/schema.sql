-- Extensões
create extension if not exists "uuid-ossp";

-- Empresa
create table if not exists empresas (
  id          uuid primary key default uuid_generate_v4(),
  nome        text not null,
  cnpj        text unique not null,
  setor       text,
  regime      text not null default 'LUCRO_PRESUMIDO',
  consolidada boolean not null default false,
  criado_em   timestamptz not null default now()
);

-- Metas mensais (cadastradas pelos sócios)
create table if not exists metas (
  id           uuid primary key default uuid_generate_v4(),
  empresa_id   uuid not null references empresas(id) on delete cascade,
  competencia  text not null,           -- formato 'YYYY-MM'
  faturamento  numeric(15,2),
  despesas     numeric(15,2),
  resultado    numeric(15,2),
  margem       numeric(6,4),            -- ex: 0.55 = 55%
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  unique(empresa_id, competencia)
);

-- Uploads de documentos
create table if not exists uploads (
  id              uuid primary key default uuid_generate_v4(),
  empresa_id      uuid not null references empresas(id) on delete cascade,
  competencia     text not null,
  tipo_doc        text not null,        -- 'DRE' | 'BALANCETE' | 'DRE+BALANCETE'
  consolidado     boolean not null default false,
  status          text not null default 'PROCESSANDO',
  confianca_ia    numeric(4,3),
  versao          int not null default 1,
  criado_em       timestamptz not null default now(),
  unique(empresa_id, competencia)
);
create index if not exists idx_uploads_empresa_competencia on uploads(empresa_id, competencia);

-- Dados financeiros extraídos
create table if not exists demonstrativos (
  id           uuid primary key default uuid_generate_v4(),
  upload_id    uuid not null references uploads(id) on delete cascade,
  empresa_id   uuid not null references empresas(id) on delete cascade,
  competencia  text not null,
  tipo         text not null,
  dados_json   jsonb not null,          -- JSON completo extraído pela IA
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);
create index if not exists idx_demonstrativos_empresa_competencia on demonstrativos(empresa_id, competencia);

-- KPIs calculados
create table if not exists kpis (
  id               uuid primary key default uuid_generate_v4(),
  empresa_id       uuid not null references empresas(id) on delete cascade,
  demonstrativo_id uuid not null references demonstrativos(id) on delete cascade,
  competencia      text not null,
  categoria        text not null,       -- 'RESULTADO' | 'DESPESAS' | 'LIQUIDEZ' | 'CRESCIMENTO'
  nome             text not null,
  valor            numeric(20,6),
  variacao_mom     numeric(10,6),
  variacao_yoy     numeric(10,6),
  pl_negativo      boolean not null default false,
  criado_em        timestamptz not null default now()
);
create index if not exists idx_kpis_empresa_competencia on kpis(empresa_id, competencia);
create index if not exists idx_kpis_empresa_nome on kpis(empresa_id, nome);

-- Alertas gerados automaticamente
create table if not exists alertas (
  id           uuid primary key default uuid_generate_v4(),
  empresa_id   uuid not null references empresas(id) on delete cascade,
  competencia  text not null,
  tipo         text not null,
  mensagem     text not null,
  detalhe      text,
  severidade   text not null,           -- 'CRITICO' | 'ALTO' | 'MEDIO' | 'INFO' | 'POSITIVO'
  lido         boolean not null default false,
  criado_em    timestamptz not null default now()
);
create index if not exists idx_alertas_empresa_competencia on alertas(empresa_id, competencia);
