import streamlit as st
from datetime import datetime
from lib.db import buscar_empresa_principal, upsert_meta
from lib.utils import MESES_PT

st.title("🎯 Metas Mensais")
st.caption("Cadastre as metas de faturamento, despesas e resultado esperado.")

empresa = buscar_empresa_principal()
if not empresa:
    st.error("Empresa não cadastrada.")
    st.stop()

col1, col2 = st.columns([1, 1])
with col1:
    ano = st.selectbox("Ano", [2024, 2025, 2026], index=2)
with col2:
    mes = st.selectbox("Mês", list(MESES_PT.keys()),
                       format_func=lambda m: MESES_PT[m],
                       index=datetime.now().month - 1)

competencia = f"{ano}-{mes:02d}"

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    faturamento = st.number_input(
        "💰 Faturamento Meta (R$)",
        min_value=0.0,
        step=1000.0,
        value=500000.0
    )
with col2:
    despesas = st.number_input(
        "💸 Despesas Meta (R$)",
        min_value=0.0,
        step=1000.0,
        value=200000.0
    )
with col3:
    resultado = st.number_input(
        "📊 Resultado Meta (R$)",
        min_value=-999999.0,
        step=1000.0,
        value=300000.0
    )

margem = (resultado / faturamento) if faturamento > 0 else 0.0

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.metric("Margem Meta", f"{margem*100:.1f}%")
with col2:
    if st.button("✅ Salvar Meta", type="primary", use_container_width=True):
        dados = {
            'faturamento': faturamento,
            'despesas': despesas,
            'resultado': resultado,
            'margem': margem
        }
        upsert_meta(empresa['id'], competencia, dados)
        st.success(f"✅ Meta salva para {competencia}")

st.markdown("---")
st.info("💡 As metas são usadas para comparações no dashboard e gráficos de performance.")
