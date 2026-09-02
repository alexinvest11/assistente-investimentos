"""
Lógica de seleção das dicas do dia.
Foco em potencial de valorização e dividendos (quando aplicável).
Gera também um resumo explicando o porquê da indicação.
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
    """Gera um resumo curto em português explicando o porquê da indicação."""
    if not asset:
        return "Nenhuma indicação disponível."

    name = asset.get("name") or asset.get("ticker")
    ticker = asset.get("ticker")
    change = asset.get("change_pct") or 0
    dy = asset.get("dividend_yield")

    if is_crypto:
        if change > 5:
            motivo = f"apresentou forte alta de {change:.1f}% no período recente"
        elif change > 2:
            motivo = f"mostra momentum positivo de {change:.1f}%"
        else:
            motivo = f"teve variação de {change:.1f}%"

        return (
            f"{name} ({ticker}) foi selecionado porque {motivo}. "
            f"Entre as principais criptomoedas monitoradas, apresentou o melhor desempenho no momento."
        )

    partes = []
    if dy and dy > 0.05:
        partes.append(f"oferece Dividend Yield atrativo de {dy*100:.1f}%")
    elif dy and dy > 0.03:
        partes.append(f"paga dividendos de {dy*100:.1f}% ao ano")

    if change > 2:
        partes.append(f"mostra valorização recente de {change:.1f}%")
    elif change > 0:
        partes.append(f"está com leve alta de {change:.1f}%")
    elif change > -2:
        partes.append("preço estável no curto prazo")

    if not partes:
        partes.append("apresentou o melhor equilíbrio entre dividendos e momentum entre os ativos analisados")

    motivo = " e ".join(partes)
    return (
        f"{name} ({ticker}) foi a melhor opção do dia porque {motivo}. "
        f"A seleção considera Dividend Yield, variação recente de preço e liquidez."
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
    all_assets = stocks + fiis
    return pick_best(all_assets, score_dividend_asset)


def analyze_usa() -> Optional[Dict]:
    stocks = get_multiple(US_STOCKS)
    reits = get_multiple(US_REITS)
    all_assets = stocks + reits
    return pick_best(all_assets, score_dividend_asset)


def analyze_europe() -> Optional[Dict]:
    stocks = get_multiple(EUROPE_STOCKS)
    return pick_best(stocks, score_dividend_asset)


def analyze_crypto() -> Optional[Dict]:
    cryptos = get_multiple(CRYPTO)
    best = pick_best(cryptos, score_crypto, is_crypto=True)
    if best and (best.get("change_pct") or 0) > 1.5:
        return best
    return None
