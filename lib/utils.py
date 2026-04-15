def fmt_brl(valor: float | None, abreviar: bool = False) -> str:
    """Formata valor como moeda brasileira."""
    if valor is None:
        return "──"
    if abreviar:
        if abs(valor) >= 1_000_000:
            return f"R$ {valor/1_000_000:.1f}M"
        if abs(valor) >= 1_000:
            return f"R$ {valor/1_000:.0f}k"
    return f"R$ {valor:_.2f}".replace("_", ".").replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(valor: float | None, sinal: bool = True) -> str:
    """Formata percentual com sinal explícito."""
    if valor is None:
        return "──"
    s = "+" if sinal and valor > 0 else ""
    return f"{s}{valor*100:.1f}%"

def cor_saldo(valor: float | None, grupo: str = "RESULTADO") -> str:
    """
    Retorna cor CSS baseada no valor e tipo de grupo.
    Para DESPESAS: gastar menos que a meta é positivo.
    Para RESULTADO e FATURAMENTO: realizar mais é positivo.
    """
    if valor is None:
        return "gray"
    if grupo == "DESPESAS":
        return "green" if valor >= 0 else "red"
    return "green" if valor >= 0 else "red"

def icone_pct(realizado: float | None, meta: float | None, grupo: str = "RESULTADO") -> str:
    """Ícone visual baseado no atingimento da meta."""
    if realizado is None or meta is None or meta == 0:
        return "──"
    pct = realizado / meta
    if grupo == "DESPESAS":
        if pct <= 0.95: return "🟢"
        if pct <= 1.05: return "✅"
        if pct <= 1.15: return "🟡"
        return "🔴"
    else:
        if pct >= 1.05: return "🟢"
        if pct >= 0.95: return "✅"
        if pct >= 0.85: return "🟡"
        return "🔴"

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

def competencia_para_label(comp: str) -> str:
    """'2026-02' → 'Fev/26'"""
    ano, mes = comp.split("-")
    return f"{MESES_PT[int(mes)]}/{ano[2:]}"
