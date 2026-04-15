def avaliar_alertas(kpis: dict, confianca_ia: float | None = None) -> list[dict]:
    """
    Gera lista de alertas baseada nos KPIs calculados.
    Mensagens em linguagem simples para sócios não-financeiros.
    """
    alertas = []

    def add(tipo, severidade, mensagem, detalhe=""):
        alertas.append({
            "tipo": tipo,
            "severidade": severidade,
            "mensagem": mensagem,
            "detalhe": detalhe
        })

    lc = kpis.get('liquidez_corrente')
    ml = kpis.get('margem_liquida')
    pt = kpis.get('pct_terceiros')
    pl_neg = kpis.get('pl_negativo', False)

    # Liquidez
    if lc is not None:
        if lc < 0.6:
            add("LIQUIDEZ", "CRITICO",
                f"⛔ Caixa em situação crítica: para cada R$1,00 de conta a pagar, há apenas R${lc:.2f} disponível",
                "Liquidez corrente abaixo de 0,60. Risco de não conseguir pagar contas em dia.")
        elif lc < 1.0:
            add("LIQUIDEZ", "ALTO",
                f"⚠️ Atenção ao caixa: a empresa tem R${lc:.2f} disponível para cada R$1,00 de obrigações imediatas",
                "Liquidez corrente abaixo de 1,0. Monitorar de perto. Ideal: acima de 1,0.")

    # Margem líquida
    if ml is not None:
        if ml < 0:
            add("RESULTADO", "CRITICO",
                f"⛔ A empresa gastou mais do que faturou: prejuízo de {abs(ml)*100:.1f}% do faturamento",
                "Resultado negativo no período.")
        elif ml < 0.1:
            add("RESULTADO", "ALTO",
                f"⚠️ Margem muito apertada: apenas {ml*100:.1f}% do faturamento virou lucro",
                "Margem líquida abaixo de 10%. Revisar estrutura de custos.")
        elif ml > 0.50:
            add("RESULTADO", "POSITIVO",
                f"✅ Ótimo resultado: {ml*100:.1f}% do faturamento virou lucro este mês",
                "Margem líquida acima de 50% é excelente para empresas de serviços.")

    # Terceiros
    if pt is not None and pt > 0.20:
        add("DESPESAS", "MEDIO",
            f"🟡 Gastos com prestadores externos representam {pt*100:.1f}% do faturamento — acima do limite de 20%",
            "Avaliar se contratos com terceiros podem ser otimizados.")

    # PL negativo
    if pl_neg:
        add("PL_NEGATIVO", "INFO",
            "ℹ️ A empresa acumulou mais dívidas do que patrimônio — isso é comum em startups com aportes de investidores",
            "Patrimônio Líquido negativo. Acompanhar evolução mensal do prejuízo acumulado.")

    # Confiança da IA
    if confianca_ia is not None and confianca_ia < 0.85:
        add("CONFIANCA_IA", "MEDIO",
            f"🟡 Leitura automática com confiança de {confianca_ia*100:.0f}% — revise os valores manualmente",
            "Documentos escaneados ou com formatação irregular podem ter extração imprecisa.")

    return alertas
