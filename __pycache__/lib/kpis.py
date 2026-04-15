def calcular_kpis(dados: dict, anterior: dict | None = None) -> dict[str, float | None]:
    """
    Calcula todos os KPIs a partir do JSON extraído.
    IMPORTANTE: Para Lucro Presumido, IR e CSLL já foram deduzidos ANTES
    da receita líquida. Não usar lucro_liquido como base para EBITDA.
    """
    dre = dados.get('dre', {})
    bp_ativo = dados.get('bp_ativo', {})
    bp_passivo = dados.get('bp_passivo', {})

    rl   = dre.get('receita_liquida')
    ll   = dre.get('lucro_liquido')
    ro   = dre.get('resultado_operacional')
    lb   = dre.get('lucro_bruto')
    dep  = (dre.get('despesas_operacionais', {})
               .get('administrativas', {})
               .get('depreciacao_amortizacao')) or 0

    desp_op  = dre.get('despesas_operacionais', {})
    pessoal  = desp_op.get('administrativas', {}).get('pessoal', {}).get('total')
    terceiros = desp_op.get('administrativas', {}).get('servicos_terceiros')
    sistemas  = desp_op.get('administrativas', {}).get('cessao_uso_sistemas')
    total_op  = desp_op.get('total_despesas_operacionais')

    ac = (bp_ativo.get('circulante') or {}).get('total')
    pc = (bp_passivo.get('circulante') or {}).get('total')
    caixa = ((bp_ativo.get('circulante') or {}).get('caixa_bancos') or 0) + \
            ((bp_ativo.get('circulante') or {}).get('aplicacoes_financeiras') or 0)
    emp_lp = ((bp_passivo.get('nao_circulante') or {}).get('emprestimos_lp') or 0) + \
             ((bp_passivo.get('nao_circulante') or {}).get('financiamentos_lp') or 0)
    pl = (bp_passivo.get('patrimonio_liquido') or {}).get('total')

    def safe_div(n, d):
        if n is None or d is None or d == 0:
            return None
        return round(n / d, 6)

    kpis = {
        # Resultado
        'margem_bruta':       safe_div(lb, rl),
        'margem_operacional': safe_div(ro, rl),
        'margem_liquida':     safe_div(ll, rl),
        'ebitda':             (ro + dep) if ro is not None else None,
        'margem_ebitda':      safe_div((ro + dep) if ro is not None else None, rl),
        'receita_liquida':    rl,
        'lucro_liquido':      ll,
        'resultado_operacional': ro,

        # Estrutura de custos (% sobre receita líquida)
        'pct_pessoal':        safe_div(pessoal, rl),
        'pct_terceiros':      safe_div(terceiros, rl),
        'pct_sistemas':       safe_div(sistemas, rl),
        'pct_total_despesas': safe_div(total_op, rl),
        'despesas_totais':    total_op,
        'despesas_pessoal':   pessoal,
        'despesas_terceiros': terceiros,

        # Liquidez (se balanço disponível)
        'liquidez_corrente':  safe_div(ac, pc),
        'caixa_disponivel':   caixa if caixa > 0 else None,
        'divida_lp_total':    emp_lp if emp_lp > 0 else None,
        'pl_negativo':        pl < 0 if pl is not None else False,
        'pl_total':           pl,
    }

    # Crescimento MoM (requer mês anterior)
    if anterior:
        dre_ant = anterior.get('dre', {})
        rl_ant = dre_ant.get('receita_liquida')
        ll_ant = dre_ant.get('lucro_liquido')
        kpis['crescimento_receita_mom'] = safe_div(
            (rl - rl_ant) if rl and rl_ant else None, rl_ant
        )
        kpis['crescimento_lucro_mom'] = safe_div(
            (ll - ll_ant) if ll and ll_ant else None, ll_ant
        )

    return kpis
