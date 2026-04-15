import streamlit as st

st.set_page_config(
    page_title="FinSight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para aproximar do design Finova
st.markdown("""
<style>
    /* Sidebar escura */
    [data-testid="stSidebar"] {
        background-color: #0f1117;
    }
    [data-testid="stSidebar"] * {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
        color: white !important;
    }

    /* Cards com sombra suave */
    [data-testid="metric-container"] {
        background-color: white;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    /* Tipografia */
    h1, h2, h3 { font-family: 'Sora', sans-serif; }
    .main { font-family: 'DM Sans', sans-serif; }

    /* Remover rodapé Streamlit */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

from lib.db import buscar_empresa_principal

empresa = buscar_empresa_principal()

if empresa:
    st.sidebar.title("📊 FinSight")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{empresa['nome']}**")
    st.sidebar.caption(f"CNPJ: {empresa['cnpj']}")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/1_Dashboard.py",  label="Visão Geral",  icon="📈")
    st.sidebar.page_link("pages/2_Importar.py",   label="Importar",     icon="📄")
    st.sidebar.page_link("pages/3_Metas.py",      label="Metas",        icon="🎯")
    st.sidebar.page_link("pages/4_Historico.py",  label="Histórico",    icon="🗂️")
    st.sidebar.markdown("---")
    st.sidebar.caption("⚙️ Configurações em breve")

    # Redirecionar para o dashboard
    st.switch_page("pages/1_Dashboard.py")
else:
    st.title("📊 FinSight")
    st.error("Nenhuma empresa cadastrada. Execute o script de seed: `python sql/seed.py`")
