"""
Análise separada: Ações Brasil, FIIs e Criptomoedas.
Inclui notícias no texto explicativo (linguagem simples).
"""
from typing import List, Dict, Optional
from core.data_collectors import (
    get_multiple,
    BRAZIL_STOCKS,
    BRAZIL_FIIS,
    CRYPTO,
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

    if asset.get("news"):
        score += 5

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

    if asset.get("news"):
        score += 5

    return score


def _news_snippet(asset: Dict) -> str:
    news = asset.get("news") or []
    if not news:
        return ""
    headline = news[0]
    if len(headline) > 120:
        headline = headline[:117] + "..."
    return f' Nas notícias recentes: "{headline}".'


def generate_reason(asset: Dict, kind: str = "stock") -> str:
    """Texto simples para leigos, com notícias quando houver."""
    if not asset:
        return "Nenhuma indicação disponível no momento."

    name = asset.get("name") or asset.get("ticker")
    ticker = asset.get("ticker")
    change = asset.get("change_pct") or 0
    dy = asset.get("dividend_yield")
    news_part = _news_snippet(asset)

    if kind == "crypto":
        if change > 5:
            base = (
                f"{name} ({ticker}) subiu bastante nos últimos dias ({change:.1f}%). "
                f"Por isso chamou atenção entre as principais criptomoedas."
            )
        elif change > 2:
            base = (
                f"{name} ({ticker}) está em alta de {change:.1f}%. "
                f"Foi a que teve melhor movimento entre as criptomoedas acompanhadas."
            )
        else:
            base = (
                f"{name} ({ticker}) teve variação de {change:.1f}%. "
                f"Foi destacada entre as principais criptomoedas do momento."
            )
        return (
            base
            + news_part
            + " Lembre-se: criptomoedas oscilam muito e o risco é alto. "
            "Isso não é recomendação de compra."
        )

    if kind == "fii":
        artigo = "O fundo imobiliário"
        quem = "cotistas"
    else:
        artigo = "A ação"
        quem = "acionistas"

    partes = []

    if dy and dy >= 0.06:
        partes.append(
            f"distribui uma boa parte do resultado aos {quem} "
            f"(cerca de {dy*100:.1f}% ao ano)"
        )
    elif dy and dy >= 0.03:
        partes.append(f"paga cerca de {dy*100:.1f}% ao ano em proventos")

    if change > 2:
        partes.append(f"o preço subiu {change:.1f}% recentemente")
    elif change > 0:
        partes.append(f"o preço está em leve alta ({change:.1f}%)")
    elif change > -2:
        partes.append("o preço está relativamente estável")

    if not partes:
        base = (
            f"{artigo} {name} ({ticker}) foi o que se saiu melhor neste momento "
            f"entre as opções analisadas, olhando proventos e comportamento do preço."
        )
    else:
        motivo = partes[0] if len(partes) == 1 else partes[0] + " e " + partes[1]
        base = f"{artigo} {name} ({ticker}) foi destacada porque {motivo}."

    return (
        base
        + news_part
        + " Isso não é uma recomendação de compra — é só um destaque automático para você avaliar."
    )


def pick_best(assets: List[Dict], scorer, kind: str = "stock") -> Optional[Dict]:
    if not assets:
        return None
    scored = [(scorer(a), a) for a in assets]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_asset = scored[0]
    best_asset["score"] = round(best_score, 1)
    best_asset["reason"] = generate_reason(best_asset, kind=kind)
    best_asset["kind"] = kind
    return best_asset


def analyze_stocks() -> Optional[Dict]:
    stocks = get_multiple(BRAZIL_STOCKS, with_news=True)
    return pick_best(stocks, score_dividend_asset, kind="stock")


def analyze_fiis() -> Optional[Dict]:
    fiis = get_multiple(BRAZIL_FIIS, with_news=True)
    return pick_best(fiis, score_dividend_asset, kind="fii")


def analyze_crypto() -> Optional[Dict]:
    cryptos = get_multiple(CRYPTO, with_news=True)
    best = pick_best(cryptos, score_crypto, kind="crypto")
    if best and (best.get("change_pct") or 0) > 1.0:
        return best
    return None
