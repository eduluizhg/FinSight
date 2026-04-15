import streamlit as st
import pandas as pd
from datetime import datetime
from lib.db import (buscar_empresa_principal, buscar_demonstrativos_ano,
                    buscar_metas_ano, buscar_kpis_periodo, buscar_alertas_nao_lidos)
from lib.utils import fmt_brl, fmt_pct, icone_pct, competencia_para_label, MESES_PT
from components.kpi_cards import render_kpi_cards
from components.tabela_resumo import render_tabela_resumo
from components.grafico_evolucao import render_grafico_evolucao
from components.alertas_feed import render_alertas_feed

st.title("📈 Visão Geral")

empresa = buscar_empresa_principal()
if not empresa:
    st.error("Empresa não encontrada.")
    st.stop()

# --- Seletor de ano ---
ano_atual = datetime.now().year
col1, col2, _ = st.columns([1, 1, 4])
with col1:
    ano = st.selectbox("Ano", options=[ano_atual - 1, ano_atual, ano_atual + 1],
                       index=1, label_visibility="collapsed")
with col2:
    mes_atual = datetime.now().month
    mes_selecionado = st.selectbox(
        "Mês de referência",
        options=list(MESES_PT.keys()),
        format_func=lambda m: MESES_PT[m],
        index=mes_atual - 1,
        label_visibility="collapsed"
    )

competencia_ref = f"{ano}-{mes_selecionado:02d}"

# --- Carregar dados ---
demonstrativos = buscar_demonstrativos_ano(empresa['id'], ano)
metas = buscar_metas_ano(empresa['id'], ano)
kpis_ref = buscar_kpis_periodo(empresa['id'], competencia_ref)
alertas = buscar_alertas_nao_lidos(empresa['id'])

# --- Alertas no topo ---
if alertas:
    render_alertas_feed(alertas[:3])  # Mostrar os 3 mais recentes
    with st.expander(f"Ver todos os {len(alertas)} alertas"):
        render_alertas_feed(alertas)

st.markdown("---")

# --- KPI Cards ---
meta_ref = metas.get(competencia_ref, {})
render_kpi_cards(kpis_ref, meta_ref)

st.markdown("---")

# --- Tabela resumo mensal ---
st.subheader("Resultado por Mês")
st.caption("Verde = no alvo ou melhor  |  Vermelho = abaixo do esperado  |  ── = sem dados")
render_tabela_resumo(demonstrativos, metas, ano)

st.markdown("---")

# --- Gráfico de evolução ---
st.subheader("Evolução do Ano")
render_grafico_evolucao(demonstrativos, metas, ano)
