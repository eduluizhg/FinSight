import google.generativeai as genai
import streamlit as st
import json
import re
import pdfplumber
import pandas as pd
from io import BytesIO

SYSTEM_PROMPT = """
Você é um especialista em contabilidade brasileira com domínio dos regimes de
Lucro Presumido e Lucro Real. Analise o documento financeiro e extraia os dados
em JSON estruturado.

REGRAS CRÍTICAS:

1. Valores: float com 2 casas decimais (686553.84). Remova pontos de milhar,
   converta vírgula decimal em ponto. Deduções e despesas são POSITIVOS no JSON.

2. Regime Lucro Presumido (IR e CSLL aparecem ANTES da Receita Líquida):
   extrair exatamente como está. NÃO mover IR/CSLL para abaixo do LAIR.

3. Balancete tem saldos ACUMULADOS. DRE do mês é fonte primária para resultado.
   Se só o balancete for enviado, usar colunas de débito/crédito do período.

4. Se campo não existir: retornar null. Nunca inventar valores.

5. Detectar unidade (reais/milhares/milhões) e converter tudo para REAIS.

6. Retornar APENAS o JSON, sem markdown, sem explicação.

SCHEMA:
{
  "tipo_documento": "DRE" | "BALANCETE" | "DRE+BALANCETE" | "BP",
  "regime_tributario": "LUCRO_PRESUMIDO" | "LUCRO_REAL" | "SIMPLES" | "DESCONHECIDO",
  "competencia": "YYYY-MM",
  "empresa_nome": string | null,
  "cnpj": string | null,
  "consolidado": boolean,
  "unidade": "REAIS" | "MILHARES" | "MILHOES",
  "dre": {
    "receita_bruta_total": number | null,
    "deducoes_receita": {
      "iss": number | null,
      "cofins": number | null,
      "pis": number | null,
      "contribuicao_social_csll": number | null,
      "imposto_renda": number | null,
      "outras_deducoes": number | null,
      "total_deducoes": number | null
    },
    "receita_liquida": number | null,
    "custo_servicos_prestados": number | null,
    "custo_mercadorias_vendidas": number | null,
    "custo_total": number | null,
    "lucro_bruto": number | null,
    "despesas_operacionais": {
      "vendas": {
        "publicidade_propaganda": number | null,
        "comissoes": number | null,
        "outras_vendas": number | null,
        "total": number | null
      },
      "administrativas": {
        "pessoal": {
          "salarios": number | null,
          "pro_labore": number | null,
          "ferias": number | null,
          "decimo_terceiro": number | null,
          "inss": number | null,
          "fgts": number | null,
          "alimentacao": number | null,
          "vale_transporte": number | null,
          "outros_pessoal": number | null,
          "total": number | null
        },
        "servicos_terceiros": number | null,
        "cessao_uso_sistemas": number | null,
        "depreciacao_amortizacao": number | null,
        "viagens": number | null,
        "alugueis_condominios": number | null,
        "telefone_internet": number | null,
        "assistencia_contabil": number | null,
        "seguros": number | null,
        "mensalidades_anuidades": number | null,
        "confraternizacao_eventos": number | null,
        "outros_administrativos": number | null,
        "total": number | null
      },
      "total_despesas_operacionais": number | null
    },
    "resultado_operacional": number | null,
    "resultado_financeiro": {
      "receitas_financeiras": number | null,
      "despesas_financeiras": number | null,
      "liquido": number | null
    },
    "outras_receitas_despesas": number | null,
    "lucro_liquido": number | null
  },
  "bp_ativo": {
    "circulante": {
      "caixa_bancos": number | null,
      "aplicacoes_financeiras": number | null,
      "contas_receber": number | null,
      "estoques": number | null,
      "tributos_recuperar": number | null,
      "outros_circulante": number | null,
      "total": number | null
    },
    "nao_circulante": {
      "adiantamentos_socios": number | null,
      "investimentos": number | null,
      "imobilizado_liquido": number | null,
      "intangivel_liquido": number | null,
      "total": number | null
    },
    "total_ativo": number | null
  },
  "bp_passivo": {
    "circulante": {
      "fornecedores": number | null,
      "obrigacoes_tributarias": number | null,
      "obrigacoes_trabalhistas": number | null,
      "provisoes": number | null,
      "outras_obrigacoes_cp": number | null,
      "total": number | null
    },
    "nao_circulante": {
      "emprestimos_lp": number | null,
      "financiamentos_lp": number | null,
      "total": number | null
    },
    "patrimonio_liquido": {
      "capital_social": number | null,
      "prejuizos_acumulados": number | null,
      "total": number | null
    },
    "total_passivo_pl": number | null
  },
  "observacoes": string | null,
  "confianca_extracao": number
}
"""

def extrair_texto_pdf(arquivo: BytesIO) -> str:
    """Extrai todo o texto de um PDF usando pdfplumber."""
    texto = []
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto.append(t)
    return "\n".join(texto)

def extrair_texto_xlsx(arquivo: BytesIO) -> str:
    """Converte XLSX/CSV em texto tabular para enviar ao Claude."""
    try:
        df = pd.read_excel(arquivo, header=None)
    except Exception:
        arquivo.seek(0)
        df = pd.read_csv(arquivo, header=None)
    return df.to_string(index=False)

def limpar_json(texto: str) -> str:
    """Remove markdown e extrai apenas o bloco JSON da resposta."""
    # Remover blocos de código markdown
    texto = re.sub(r'```(?:json)?', '', texto).strip()
    # Extrair primeiro objeto JSON válido
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        return match.group(0)
    return texto

def extrair_dados(arquivo: BytesIO, nome_arquivo: str) -> dict:
    """
    Pipeline completo de extração:
    1. Ler arquivo (PDF ou XLSX)
    2. Enviar texto ao Claude
    3. Parsear JSON da resposta
    4. Validar campos críticos
    5. Retornar dados estruturados
    """
    # 1. Extrair texto conforme tipo de arquivo
    if nome_arquivo.lower().endswith('.pdf'):
        texto = extrair_texto_pdf(arquivo)
    elif nome_arquivo.lower().endswith(('.xlsx', '.xls')):
        texto = extrair_texto_xlsx(arquivo)
    elif nome_arquivo.lower().endswith('.csv'):
        texto = extrair_texto_xlsx(arquivo)
    else:
        raise ValueError(f"Formato não suportado: {nome_arquivo}")

    if not texto.strip():
        raise ValueError("Não foi possível extrair texto do arquivo. Verifique se o PDF não é uma imagem escaneada sem OCR.")

    # 2. Chamar Gemini API
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')

    prompt_completo = f"{SYSTEM_PROMPT}\n\nExtraía os dados financeiros do documento abaixo:\n\n{texto}"
    
    resposta = model.generate_content(prompt_completo)
    texto_resposta = resposta.text

    # 3. Parsear JSON
    try:
        json_limpo = limpar_json(texto_resposta)
        dados = json.loads(json_limpo)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude retornou resposta inválida. Tente novamente. Erro: {e}")

    # 4. Validar campos críticos
    dre = dados.get('dre', {})
    if dre.get('receita_liquida') is None and dre.get('receita_bruta_total') is None:
        dados['confianca_extracao'] = min(dados.get('confianca_extracao', 0.5), 0.5)

    # 5. Marcar para revisão se confiança baixa
    if dados.get('confianca_extracao', 1.0) < 0.85:
        dados['_requer_revisao'] = True

    return dados
