import streamlit as st
from lib.db import buscar_empresa_principal
from lib.utils import fmt_brl, MESES_PT
import pandas as pd

st.title("🗂️ Histórico de Uploads")
st.caption("Visualize todos os documentos processados e seus status.")

empresa = buscar_empresa_principal()
if not empresa:
    st.error("Empresa não cadastrada.")
    st.stop()

# Buscar uploads
with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.id, u.competencia, u.tipo_doc, u.status, u.confianca_ia, u.criado_em,
                   d.dados_json
            FROM uploads u
            LEFT JOIN demonstrativos d ON d.upload_id = u.id
            WHERE u.empresa_id = %s
            ORDER BY u.criado_em DESC
        """, (empresa['id'],))
        uploads = cur.fetchall()

if not uploads:
    st.info("Nenhum documento processado ainda.")
    st.stop()

# Converter para DataFrame
df_uploads = []
for u in uploads:
    dados_json = u.get('dados_json', {})
    dre = dados_json.get('dre', {}) if dados_json else {}
    
    df_uploads.append({
        'Competência': u['competencia'],
        'Tipo': u['tipo_doc'],
        'Status': u['status'],
        'Confiança IA': f"{u['confianca_ia']*100:.0f}%" if u['confianca_ia'] else "──",
        'Faturamento': fmt_brl(dre.get('receita_liquida')),
        'Lucro': fmt_brl(dre.get('lucro_liquido')),
        'Data Upload': u['criado_em'].strftime('%d/%m/%Y %H:%M') if u['criado_em'] else "──",
    })

df = pd.DataFrame(df_uploads)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.info("💡 Clique na linha para expandir detalhes do documento. Status: CONCLUIDO (pronto) | REVISAO_MANUAL (revisar valores)")
