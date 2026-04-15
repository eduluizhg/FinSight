import streamlit as st
from lib.utils import fmt_brl, fmt_pct

def render_kpi_cards(kpis: dict, meta: dict):
    """
    Exibe 6 cards com KPIs principais.
    Layout: 3 colunas × 2 linhas.
    """
    col1, col2, col3 = st.columns(3)
    
    # Linha 1
    with col1:
        faturamento = kpis.get('receita_liquida')
        meta_fat = meta.get('faturamento')
        st.metric(
            "📊 Faturamento",
            fmt_brl(faturamento, abreviar=True),
            f"{fmt_pct((faturamento - meta_fat) / meta_fat) if meta_fat else '──'}" if meta_fat and faturamento else "──"
        )
    
    with col2:
        lucro = kpis.get('lucro_liquido')
        meta_lucro = meta.get('resultado')
        st.metric(
            "💰 Lucro Líquido",
            fmt_brl(lucro, abreviar=True),
            f"{fmt_pct((lucro - meta_lucro) / meta_lucro) if meta_lucro else '──'}" if meta_lucro and lucro else "──"
        )
    
    with col3:
        margem = kpis.get('margem_liquida')
        st.metric(
            "📈 Margem Líquida",
            fmt_pct(margem, sinal=False) if margem else "──",
            delta=None
        )
    
    # Linha 2
    col4, col5, col6 = st.columns(3)
    
    with col4:
        despesas = kpis.get('despesas_totais')
        meta_desp = meta.get('despesas')
        st.metric(
            "💸 Despesas",
            fmt_brl(despesas, abreviar=True),
            f"{fmt_pct((despesas - meta_desp) / meta_desp) if meta_desp else '──'}" if meta_desp and despesas else "──"
        )
    
    with col5:
        lc = kpis.get('liquidez_corrente')
        cor = "🟢" if lc and lc >= 1.0 else "🟡" if lc and lc >= 0.6 else "🔴"
        st.metric(
            "💧 Liquidez",
            f"{cor} {lc:.2f}" if lc else "──",
            delta=None
        )
    
    with col6:
        pessoal_pct = kpis.get('pct_pessoal')
        st.metric(
            "👥 % Pessoal",
            fmt_pct(pessoal_pct, sinal=False) if pessoal_pct else "──",
            delta=None
        )
