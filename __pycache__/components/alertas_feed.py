import streamlit as st

def render_alertas_feed(alertas: list):
    """
    Exibe feed de alertas com cores baseadas em severidade.
    """
    if not alertas:
        st.info("✅ Nenhum alerta ativo")
        return
    
    for alerta in alertas:
        severidade = alerta.get('severidade', 'INFO')
        mensagem = alerta.get('mensagem', '')
        detalhe = alerta.get('detalhe', '')
        
        if severidade == "CRITICO":
            st.error(f"**{mensagem}**\n\n{detalhe}")
        elif severidade == "ALTO":
            st.warning(f"**{mensagem}**\n\n{detalhe}")
        elif severidade == "MEDIO":
            st.warning(f"**{mensagem}**\n\n{detalhe}")
        elif severidade == "POSITIVO":
            st.success(f"**{mensagem}**\n\n{detalhe}")
        else:  # INFO
            st.info(f"**{mensagem}**\n\n{detalhe}")
