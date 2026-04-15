import google.generativeai as genai
import streamlit as st
import pdfplumber
import io
import json

# Força a leitura da chave de API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Chave GEMINI_API_KEY não encontrada nos secrets.")

def extrair_dados(conteudo, nome_arquivo):
    # 1. Instancia o modelo atualizado
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 2. Extrai o texto do PDF diretamente da memória RAM do Streamlit
    texto_dre = ""
    try:
        # Transforma os bytes recebidos pelo Streamlit em um arquivo legível
        with pdfplumber.open(io.BytesIO(conteudo)) as pdf:
            for pagina in pdf.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_dre += texto_extraido + "\n"
    except Exception as e:
        st.error(f"Erro na leitura do arquivo PDF local: {e}")
        return None

    # Se a extração falhar ou o PDF for apenas uma imagem escaneada
    if not texto_dre.strip():
        st.warning("Não foi possível extrair texto do PDF. O arquivo pode ser uma imagem escaneada.")
        return None

    # 3. Constrói o prompt injetando apenas o TEXTO do documento, evitando erros 404 de File API
    prompt_completo = f"""
    Você é um analista financeiro sênior. Extraia as principais métricas financeiras (Receita, Custos, Lucro, etc.) do documento abaixo.
    Retorne o resultado EXCLUSIVAMENTE em um formato JSON válido, sem formatações markdown e sem textos adicionais.
    
    Nome do Arquivo: {nome_arquivo}
    
    Conteúdo do Documento:
    {texto_dre}
    """
    
    # 4. Envia o texto puro para o modelo
    try:
        resposta = model.generate_content(prompt_completo)
        
        # Limpa possível formatação markdown que o Gemini possa retornar
        texto_limpo = resposta.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        
        # Valida se é um JSON estruturado
        return json.loads(texto_limpo)
        
    except json.JSONDecodeError:
        st.error("A IA não retornou um formato JSON válido.")
        return None
    except Exception as e:
        st.error(f"Erro ao comunicar com o Google Gemini: {e}")
        return None
