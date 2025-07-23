def analyze_token(token):
    # Heurística simple per determinar el motiu de la pujada
    reasons = []

    volume = float(token.get("volume24h", 0))
    price_change = float(token.get("priceChangePct", 0))
    liquidity = float(token.get("liquidity", 0))

    if price_change > 50:
        reasons.append("Pujada molt forta en poc temps (possible FOMO)")
    if volume > 100_000:
        reasons.append("Volum alt indica interès dels inversors")
    if liquidity < 10_000:
        reasons.append("Baixa liquiditat (possible manipulació de preu)")
    if "NEW" in token.get("tags", ""):
        reasons.append("Token acabat de llançar")

    if not reasons:
        return "No s'ha pogut determinar un motiu clar"
    return "; ".join(reasons)