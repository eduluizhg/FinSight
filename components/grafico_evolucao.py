import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lib.utils import competencia_para_label

def render_grafico_evolucao(demonstrativos: list, metas: dict, ano: int):
    """
    Gráfico Plotly com barras (Faturamento) + linha (Margem).
    Mostra tendência de 12 meses com comparação de metas.
    """
    if not demonstrativos:
        st.warning("Sem dados disponíveis para o gráfico.")
        return

    # Preparar dados
    competencias = [d['competencia'] for d in demonstrativos]
    labels = [competencia_para_label(c) for c in competencias]
    
    faturamentos = []
    faturamentos_meta = []
    margens = []
    margens_meta = []
    
    for comp in competencias:
        d = next((x for x in demonstrativos if x['competencia'] == comp), None)
        if d:
            dj = d['dados_json'].get('dre', {})
            fat = dj.get('receita_liquida')
            faturamentos.append(fat)
            
            margem = (dj.get('lucro_liquido') / fat 
                     if fat and dj.get('lucro_liquido') is not None else None)
            margens.append(margem)
        
        meta = metas.get(comp, {})
        faturamentos_meta.append(meta.get('faturamento'))
        margens_meta.append(meta.get('margem'))
    
    # Criar gráfico com subplots
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.1
    )
    
    # Barras: Faturamento realizado
    fig.add_trace(
        go.Bar(
            x=labels,
            y=faturamentos,
            name="Faturamento",
            marker=dict(color="#2563eb", opacity=0.7),
            text=[f"R$ {v/1000:.0f}k" if v else "──" for v in faturamentos],
            textposition="outside",
            yaxis="y",
        ),
        secondary_y=False,
    )
    
    # Linha: Faturamento meta
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=faturamentos_meta,
            name="Meta Faturamento",
            mode="lines",
            line=dict(color="#2563eb", dash="dash", width=2),
            yaxis="y",
        ),
        secondary_y=False,
    )
    
    # Linha: Margem
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=[m*100 if m else None for m in margens],
            name="Margem %",
            mode="lines+markers",
            line=dict(color="#16a34a", width=3),
            marker=dict(size=8),
            yaxis="y2",
        ),
        secondary_y=True,
    )
    
    # Layout
    fig.update_layout(
        title=f"Evolução Financeira {ano}",
        hovermode="x unified",
        height=400,
        showlegend=True,
        plot_bgcolor="rgba(240, 240, 245, 0.5)",
    )
    
    fig.update_xaxes(title_text="Mês")
    fig.update_yaxes(title_text="Faturamento (R$)", secondary_y=False)
    fig.update_yaxes(title_text="Margem (%)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
