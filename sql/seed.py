"""
Script de seed — popula o banco com empresa ESG Now + 12 meses de dados.
Rodar uma única vez: python sql/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
from datetime import datetime
from lib.db import get_conn

MESES_SEED = [
    ("2025-03", 410000, 185000, 225000, 0.549, 0.52),
    ("2025-04", 440000, 195000, 245000, 0.557, 0.55),
    ("2025-05", 460000, 198000, 262000, 0.570, 0.51),
    ("2025-06", 475000, 214000, 261000, 0.550, 0.48),  # terceiros alto neste mês
    ("2025-07", 490000, 210000, 280000, 0.571, 0.53),
    ("2025-08", 505000, 208000, 297000, 0.588, 0.56),
    ("2025-09", 515000, 211000, 304000, 0.590, 0.54),
    ("2025-10", 530000, 215000, 315000, 0.594, 0.57),
    ("2025-11", 540000, 216000, 324000, 0.600, 0.55),
    ("2025-12", 548000, 214000, 334000, 0.609, 0.60),
    ("2026-01", 551000, 213000, 338000, 0.613, 0.56),
    ("2026-02", 558749, 212077, 344766, 0.617, 0.48),  # dados reais Fev/26
]

def montar_dre(faturamento, despesas, resultado):
    pessoal = despesas * 0.28
    terceiros = despesas * 0.49
    sistemas = despesas * 0.08
    outros = despesas - pessoal - terceiros - sistemas
    return {
        "receita_bruta_total": faturamento * 1.30,
        "deducoes_receita": {"total_deducoes": faturamento * 0.30},
        "receita_liquida": faturamento,
        "custo_servicos_prestados": faturamento * 0.005,
        "custo_total": faturamento * 0.005,
        "lucro_bruto": faturamento * 0.995,
        "despesas_operacionais": {
            "administrativas": {
                "pessoal": {"total": pessoal},
                "servicos_terceiros": terceiros,
                "cessao_uso_sistemas": sistemas,
                "depreciacao_amortizacao": 2789.59,
                "outros_administrativos": outros,
                "total": despesas,
            },
            "vendas": {"total": 0},
            "total_despesas_operacionais": despesas,
        },
        "resultado_operacional": resultado * 1.006,
        "resultado_financeiro": {"liquido": -1905.02},
        "lucro_liquido": resultado,
    }

def main():
    print("Configurando banco de dados...")
    print("\nℹ️  Você precisa ter configurado os secrets em .streamlit/secrets.toml")
    print("ou ter variáveis de ambiente definidas.\n")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Empresa
                print("📝 Criando empresa ESG Now...")
                cur.execute("""
                    INSERT INTO empresas (nome, cnpj, setor, regime, consolidada)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (cnpj) DO UPDATE SET nome = EXCLUDED.nome
                    RETURNING id
                """, ("ESG Now Tecnologia Ltda.", "42.993.342/0001-08",
                      "Tecnologia/ESG", "LUCRO_PRESUMIDO", True))
                empresa_id = cur.fetchone()['id']
                print(f"   ✅ Empresa criada: {empresa_id}")

                print("\n📊 Criando 12 meses de dados...")
                for i, (comp, fat, desp, res, margem, lc) in enumerate(MESES_SEED):
                    dre_json = montar_dre(fat, desp, res)
                    dados = {
                        "tipo_documento": "DRE",
                        "regime_tributario": "LUCRO_PRESUMIDO",
                        "competencia": comp,
                        "consolidado": True,
                        "dre": dre_json,
                        "confianca_extracao": 0.71 if comp == "2025-06" else 0.93,
                    }

                    # Upload
                    cur.execute("""
                        INSERT INTO uploads (empresa_id, competencia, tipo_doc, consolidado, status, confianca_ia)
                        VALUES (%s, %s, 'DRE', true, 'CONCLUIDO', %s) RETURNING id
                    """, (empresa_id, comp, dados['confianca_extracao']))
                    upload_id = cur.fetchone()['id']

                    # Demonstrativo
                    cur.execute("""
                        INSERT INTO demonstrativos (upload_id, empresa_id, competencia, tipo, dados_json)
                        VALUES (%s, %s, %s, 'DRE', %s) RETURNING id
                    """, (upload_id, empresa_id, comp, json.dumps(dados)))
                    demo_id = cur.fetchone()['id']

                    # KPIs essenciais
                    kpis = [
                        ('receita_liquida',    'RESULTADO', fat),
                        ('lucro_liquido',      'RESULTADO', res),
                        ('margem_liquida',     'RESULTADO', margem),
                        ('despesas_totais',    'DESPESAS',  desp),
                        ('pct_terceiros',      'DESPESAS',  0.22 if comp == "2025-09" else 0.187),
                        ('liquidez_corrente',  'LIQUIDEZ',  lc),
                    ]
                    for nome, cat, valor in kpis:
                        cur.execute("""
                            INSERT INTO kpis (empresa_id, demonstrativo_id, competencia, categoria, nome, valor)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (empresa_id, demo_id, comp, cat, nome, valor))

                    # Metas
                    cur.execute("""
                        INSERT INTO metas (empresa_id, competencia, faturamento, despesas, resultado, margem)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (empresa_id, competencia) DO NOTHING
                    """, (empresa_id, comp, fat * 1.05, desp * 0.97, res * 1.08, margem + 0.02))
                    
                    print(f"   ✅ {comp}: R$ {fat/1000:.0f}k faturamento, {margem*100:.1f}% margem")

        print("\n✅ Seed concluído com sucesso!")
        print("\nAgora execute: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nVerifique se:")
        print("  1. .streamlit/secrets.toml está configurado com as 4 variáveis")
        print("  2. SUPABASE_DB_URL aponta para o banco correto")
        print("  3. O schema foi executado no SQL Editor do Supabase")

if __name__ == "__main__":
    main()
