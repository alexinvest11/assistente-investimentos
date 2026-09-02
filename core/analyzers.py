"""
Lógica de seleção das dicas do dia + texto simples para leigos.
"""
from typing import List, Dict, Optional
from core.data_collectors import (
    get_multiple,
    BRAZIL_STOCKS, BRAZIL_FIIS,
    US_STOCKS, US_REITS,
    EUROPE_STOCKS, CRYPTO
)


def score_dividend_asset(asset: Dict) -> float:
    score = 0.0
    dy = asset.get("dividend_yield") or 0

    if dy:
        if dy > 0.08:
            score += 40
        elif dy > 0.05:
            score += 30
        elif dy > 0.03:
            score += 20
        else:
            score += 10

    change = asset.get("change_pct") or 0
    if change > 2:
        score += 20
    elif change > 0:
        score += 10
    elif change > -2:
        score += 5

    mcap = asset.get("market_cap") or 0
    if mcap > 50_000_000_000:
        score += 15
    elif mcap > 10_000_000_000:
        score += 10

    return score


def score_crypto(asset: Dict) -> float:
    score = 0.0
    change = asset.get("change_pct") or 0

    if change > 5:
        score += 50
    elif change > 2:
        score += 30
    elif change > 0:
        score += 15

    if asset["ticker"] == "BTC-USD":
        score += 20
    elif asset["ticker"] == "ETH-USD":
        score += 15

    return score


def generate_reason(asset: Dict, is_crypto: bool = False) -> str:
    """Texto bem simples, para quem não entende de investimentos."""
    if not asset:
        return "Nenhuma indicação disponível hoje."

    name = asset.get("name") or asset.get("ticker")
    ticker = asset.get("ticker")
    change = asset.get("change_pct") or 0
    dy = asset.get("dividend_yield")

    if is_crypto:
        if change > 5:
            return (
                f"{name} ({ticker}) subiu bastante nos últimos dias ({change:.1f}%). "
                f"Por isso chamou atenção entre as principais criptomoedas. "
                f"Lembre-se: criptomoedas oscilam muito e o risco é alto."
            )
        if change > 2:
            return (
                f"{name} ({ticker}) está em alta de {change:.1f}%. "
                f"Foi a que teve melhor movimento entre as criptomoedas acompanhadas. "
                f"Criptomoedas são voláteis — use com cuidado."
            )
        return (
            f"{name} ({ticker}) teve variação de {change:.1f}%. "
            f"Foi destacada entre as principais criptomoedas do momento."
        )

    # Ações / FIIs / REITs — linguagem leiga
    partes = []

    if dy and dy >= 0.06:
        partes.append(
            f"ela distribui uma boa parte do lucro aos acionistas "
            f"(cerca de {dy*100:.1f}% ao ano em dividendos)"
        )
    elif dy and dy >= 0.03:
        partes.append(
            f"ela paga dividendos de cerca de {dy*100:.1f}% ao ano"
        )

    if change > 2:
        partes.append(f"o preço subiu {change:.1f}% recentemente")
    elif change > 0:
        partes.append(f"o preço está em leve alta ({change:.1f}%)")
    elif change > -2:
        partes.append("o preço está relativamente estável")

    if not partes:
        return (
            f"{name} ({ticker}) foi a que se saiu melhor hoje entre as opções analisadas, "
            f"combinando pagamento de dividendos e comportamento do preço."
        )

    if len(partes) == 1:
        motivo = partes[0]
    else:
        motivo = partes[0] + " e " + partes[1]

    return (
        f"{name} ({ticker}) foi escolhida porque {motivo}. "
        f"Isso a deixou como a opção mais interessante do dia nesta carteira. "
        f"Isso não é uma recomendação de compra — é apenas um destaque automático para você avaliar."
    )


def pick_best(assets: List[Dict], scorer, is_crypto: bool = False) -> Optional[Dict]:
    if not assets:
        return None
    scored = [(scorer(a), a) for a in assets]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_asset = scored[0]
    best_asset["score"] = round(best_score, 1)
    best_asset["reason"] = generate_reason(best_asset, is_crypto=is_crypto)
    return best_asset


def analyze_brazil() -> Optional[Dict]:
    stocks = get_multiple(BRAZIL_STOCKS)
    fiis = get_multiple(BRAZIL_FIIS)
    return pick_best(stocks + fiis, score_dividend_asset)


def analyze_usa() -> Optional[Dict]:
    stocks = get_multiple(US_STOCKS)
    reits = get_multiple(US_REITS)
    return pick_best(stocks + reits, score_dividend_asset)


def analyze_europe() -> Optional[Dict]:
    stocks = get_multiple(EUROPE_STOCKS)
    return pick_best(stocks, score_dividend_asset)


def analyze_crypto() -> Optional[Dict]:
    cryptos = get_multiple(CRYPTO)
    best = pick_best(cryptos, score_crypto, is_crypto=True)
    if best and (best.get("change_pct") or 0) > 1.5:
        return best
    return None
