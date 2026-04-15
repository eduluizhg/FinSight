import streamlit as st
from supabase import create_client, Client

# ---------- Supabase client (para operações simples) ----------

@st.cache_resource
def get_supabase() -> Client:
    """
    Conexão Supabase reutilizada entre reruns do Streamlit.
    Credenciais lidas dos secrets — nunca hardcoded.
    """
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

# ---------- Helpers de consulta ----------

def buscar_empresa_principal():
    supabase = get_supabase()
    try:
        # Equivalente a: SELECT * FROM empresas LIMIT 1;
        resposta = supabase.table("empresas").select("*").limit(1).execute()
        
        if resposta.data and len(resposta.data) > 0:
            return resposta.data[0]
        return None
    except Exception as e:
        st.error(f"Erro de comunicação via API: {e}")
        return None

def buscar_demonstrativos_ano(empresa_id: str, ano: int) -> list[dict]:
    """Retorna todos os demonstrativos de um ano, ordenados por mês."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.*, u.confianca_ia, u.status, u.tipo_doc
                FROM demonstrativos d
                JOIN uploads u ON u.id = d.upload_id
                WHERE d.empresa_id = %s
                  AND d.competencia LIKE %s
                ORDER BY d.competencia
            """, (empresa_id, f"{ano}-%"))
            return cur.fetchall()

def buscar_metas_ano(empresa_id: str, ano: int) -> dict[str, dict]:
    """Retorna metas do ano indexadas por competencia ('YYYY-MM')."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM metas
                WHERE empresa_id = %s AND competencia LIKE %s
            """, (empresa_id, f"{ano}-%"))
            rows = cur.fetchall()
            return {r['competencia']: dict(r) for r in rows}

def buscar_kpis_periodo(empresa_id: str, competencia: str) -> dict[str, float | None]:
    """Retorna KPIs de um mês como dicionário nome → valor."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nome, valor FROM kpis
                WHERE empresa_id = %s AND competencia = %s
            """, (empresa_id, competencia))
            return {r['nome']: float(r['valor']) if r['valor'] is not None else None
                    for r in cur.fetchall()}

def buscar_alertas_nao_lidos(empresa_id: str) -> list[dict]:
    """Retorna alertas não marcados como lidos."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM alertas
                WHERE empresa_id = %s AND lido = false
                ORDER BY criado_em DESC
            """, (empresa_id,))
            return cur.fetchall()

def upsert_meta(empresa_id: str, competencia: str, dados: dict):
    """Insere ou atualiza meta para um período."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO metas (empresa_id, competencia, faturamento, despesas, resultado, margem)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (empresa_id, competencia)
                DO UPDATE SET
                    faturamento   = EXCLUDED.faturamento,
                    despesas      = EXCLUDED.despesas,
                    resultado     = EXCLUDED.resultado,
                    margem        = EXCLUDED.margem,
                    atualizado_em = now()
            """, (
                empresa_id, competencia,
                dados.get('faturamento'), dados.get('despesas'),
                dados.get('resultado'), dados.get('margem')
            ))
