import streamlit as st
import pandas as pd
from lib.utils import fmt_brl, fmt_pct, icone_pct, competencia_para_label, MESES_PT

def render_tabela_resumo(demonstrativos: list, metas: dict, ano: int):
    """
    Tabela principal: linhas = grupos financeiros, colunas = meses.
    Exibe Meta / Realizado / Saldo / % por grupo.
    """
    # Indexar demonstrativos por competência
    dados_por_mes = {}
    for d in demonstrativos:
        comp = d['competencia']
        dj = d['dados_json'].get('dre', {})
        desp_op = dj.get('despesas_operacionais', {})
        pessoal = desp_op.get('administrativas', {}).get('pessoal', {}).get('total')
        terceiros = desp_op.get('administrativas', {}).get('servicos_terceiros')
        dados_por_mes[comp] = {
            'faturamento':  dj.get('receita_liquida'),
            'despesas':     dj.get('despesas_operacionais', {}).get('total_despesas_operacionais'),
            'pessoal':      pessoal,
            'terceiros':    terceiros,
            'resultado':    dj.get('lucro_liquido'),
            'margem':       (dj.get('lucro_liquido') / dj.get('receita_liquida')
                             if dj.get('receita_liquida') and dj.get('lucro_liquido') else None),
        }

    # Construir linhas da tabela
    grupos = [
        ("FATURAMENTO",   "faturamento",  "RESULTADO"),
        ("DESPESAS",      "despesas",     "DESPESAS"),
        ("└ Pessoas",     "pessoal",      "DESPESAS"),
        ("└ Terceiros",   "terceiros",    "DESPESAS"),
        ("RESULTADO MÊS", "resultado",    "RESULTADO"),
        ("MARGEM",        "margem",       "RESULTADO"),
    ]

    meses_ano = [f"{ano}-{m:02d}" for m in range(1, 13)]
    labels = [competencia_para_label(c) for c in meses_ano]

    # Sublinhas: Meta / Realizado / Saldo / %
    sublinhas = ["Meta", "Realizado", "Saldo", "%"]

    linhas = []
    for grupo_nome, campo, tipo in grupos:
        for sublinha in sublinhas:
            row = {"": f"{grupo_nome} — {sublinha}"}
            total_meta = 0.0
            total_real = 0.0

            for comp, label in zip(meses_ano, labels):
                realizado = dados_por_mes.get(comp, {}).get(campo)
                meta_comp = metas.get(comp, {}).get(campo)

                if sublinha == "Meta":
                    row[label] = fmt_brl(meta_comp) if meta_comp else "──"
                    if meta_comp: total_meta += meta_comp

                elif sublinha == "Realizado":
                    row[label] = fmt_brl(realizado) if realizado else "──"
                    if realizado: total_real += realizado

                elif sublinha == "Saldo":
                    if realizado is not None and meta_comp is not None:
                        saldo = realizado - meta_comp
                        cor = "🟢" if (saldo >= 0 and tipo == "RESULTADO") or \
                                      (saldo <= 0 and tipo == "DESPESAS") else "🔴"
                        row[label] = f"{cor} {fmt_brl(saldo)}"
                    else:
                        row[label] = "──"

                elif sublinha == "%":
                    if realizado is not None and meta_comp is not None and meta_comp != 0:
                        pct = realizado / meta_comp
                        icone = icone_pct(realizado, meta_comp, tipo)
                        row[label] = f"{icone} {pct*100:.1f}%"
                    elif campo == "margem" and realizado is not None:
                        row[label] = fmt_pct(realizado, sinal=False)
                    else:
                        row[label] = "──"

            # Coluna TOTAL
            if sublinha == "Meta":
                row["Total"] = fmt_brl(total_meta) if total_meta else "──"
            elif sublinha == "Realizado":
                row["Total"] = fmt_brl(total_real) if total_real else "──"
            elif sublinha == "Saldo":
                if total_real and total_meta:
                    saldo_total = total_real - total_meta
                    cor = "🟢" if saldo_total >= 0 else "🔴"
                    row["Total"] = f"{cor} {fmt_brl(saldo_total)}"
                else:
                    row["Total"] = "──"
            elif sublinha == "%":
                if total_real and total_meta and total_meta != 0:
                    pct_total = total_real / total_meta
                    row["Total"] = f"{pct_total*100:.1f}%"
                else:
                    row["Total"] = "──"

            linhas.append(row)

    df = pd.DataFrame(linhas)

    # Estilizar separadores entre grupos
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "": st.column_config.TextColumn("", width="medium"),
            **{label: st.column_config.TextColumn(label, width="small") for label in labels},
            "Total": st.column_config.TextColumn("Total Ano", width="medium"),
        }
    )
