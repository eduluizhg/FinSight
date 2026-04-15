import streamlit as st
import json
from datetime import datetime
from lib.db import buscar_empresa_principal
from lib.extrator import extrair_dados
from lib.kpis import calcular_kpis
from lib.alertas import avaliar_alertas
from lib.utils import MESES_PT

st.title("📄 Importar Documento")
st.caption("Arraste um PDF ou XLSX do balancete ou DRE mensal.")

empresa = buscar_empresa_principal()
if not empresa:
    st.error("Empresa não cadastrada.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    ano = st.selectbox("Ano", [2024, 2025, 2026], index=2)
with col2:
    mes = st.selectbox("Mês", list(MESES_PT.keys()),
                       format_func=lambda m: MESES_PT[m],
                       index=datetime.now().month - 1)
with col3:
    tipo_doc = st.selectbox("Tipo", ["DRE+BALANCETE", "DRE", "BALANCETE", "BP"])

competencia = f"{ano}-{mes:02d}"
arquivo = st.file_uploader("Arquivo", type=["pdf", "xlsx", "xls", "csv"])

if arquivo and st.button("🤖 Processar com IA", type="primary"):
    with st.status("Processando documento...", expanded=True) as status:

        st.write("📖 Lendo o arquivo...")
        from io import BytesIO
        conteudo = BytesIO(arquivo.read())

        st.write("🧠 Extraindo dados com Claude AI...")
        try:
            dados = extrair_dados(conteudo, arquivo.name)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        st.write("📊 Calculando indicadores...")
        kpis = calcular_kpis(dados)
        alertas = avaliar_alertas(kpis, dados.get('confianca_extracao'))

        st.write("💾 Salvando no banco de dados...")
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Upload
                cur.execute("""
                    INSERT INTO uploads (empresa_id, competencia, tipo_doc, consolidado, status, confianca_ia)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """, (empresa['id'], competencia, tipo_doc,
                      dados.get('consolidado', False),
                      'REVISAO_MANUAL' if dados.get('_requer_revisao') else 'CONCLUIDO',
                      dados.get('confianca_extracao')))
                upload_id = cur.fetchone()['id']

                # Demonstrativo
                cur.execute("""
                    INSERT INTO demonstrativos (upload_id, empresa_id, competencia, tipo, dados_json)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (upload_id, empresa['id'], competencia, tipo_doc, json.dumps(dados)))
                demo_id = cur.fetchone()['id']

                # KPIs
                for nome, valor in kpis.items():
                    if isinstance(valor, bool):
                        continue
                    cur.execute("""
                        INSERT INTO kpis (empresa_id, demonstrativo_id, competencia, categoria, nome, valor)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (empresa['id'], demo_id, competencia,
                          'RESULTADO' if 'margem' in nome or 'lucro' in nome or 'receita' in nome else 'DESPESAS',
                          nome, float(valor) if valor is not None else None))

                # Alertas
                for alerta in alertas:
                    cur.execute("""
                        INSERT INTO alertas (empresa_id, competencia, tipo, mensagem, detalhe, severidade)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (empresa['id'], competencia,
                          alerta['tipo'], alerta['mensagem'],
                          alerta.get('detalhe'), alerta['severidade']))

        status.update(label="✅ Concluído!", state="complete")

    # Resumo do processamento
    dre = dados.get('dre', {})
    st.success(f"Documento processado com sucesso!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento", f"R$ {dre.get('receita_liquida', 0):,.0f}".replace(",", "."))
    col2.metric("Lucro Líquido", f"R$ {dre.get('lucro_liquido', 0):,.0f}".replace(",", "."))
    col3.metric("Alertas gerados", len(alertas))

    if dados.get('_requer_revisao'):
        st.warning(f"⚠️ Confiança da extração: {dados.get('confianca_extracao', 0)*100:.0f}% — revise os valores no dashboard")

    if st.button("📈 Ver no Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
