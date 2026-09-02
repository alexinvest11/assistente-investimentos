"""
Lógica simples de seleção das dicas do dia.
Foco em potencial de valorização e dividendos (quando aplicável).
"""
from typing import List, Dict, Optional
from core.data_collectors import (
    get_multiple, 
    BRAZIL_STOCKS, BRAZIL_FIIS,
    US_STOCKS, US_REITS,
    EUROPE_STOCKS, CRYPTO
)


def score_dividend_asset(asset: Dict) -> float:
    """Pontuação simples para ativos que pagam dividendos."""
    score = 0.0
    dy = asset.get("dividend_yield") or 0
    
    # Dividend Yield (quanto maior, melhor até certo ponto)
    if dy:
        if dy > 0.08:      # > 8%
            score += 40
        elif dy > 0.05:    # > 5%
            score += 30
        elif dy > 0.03:    # > 3%
            score += 20
        else:
            score += 10
    
    # Momentum de preço (valorização recente)
    change = asset.get("change_pct") or 0
    if change > 2:
        score += 20
    elif change > 0:
        score += 10
    elif change > -2:
        score += 5
    
    # Preferência por nomes conhecidos / liquidez (market cap)
    mcap = asset.get("market_cap") or 0
    if mcap > 50_000_000_000:
        score += 15
    elif mcap > 10_000_000_000:
        score += 10
    
    return score


def score_crypto(asset: Dict) -> float:
    """Pontuação para criptomoedas (foco em momentum)."""
    score = 0.0
    change = asset.get("change_pct") or 0
    
    if change > 5:
        score += 50
    elif change > 2:
        score += 30
    elif change > 0:
        score += 15
    
    # Preferência por maiores
    if asset["ticker"] == "BTC-USD":
        score += 20
    elif asset["ticker"] == "ETH-USD":
        score += 15
    
    return score


def pick_best(assets: List[Dict], scorer) -> Optional[Dict]:
    """Escolhe o ativo com maior pontuação."""
    if not assets:
        return None
    scored = [(scorer(a), a) for a in assets]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_asset = scored[0]
    best_asset["score"] = round(best_score, 1)
    return best_asset


def analyze_brazil() -> Optional[Dict]:
    """Retorna a melhor dica do dia para o Brasil."""
    stocks = get_multiple(BRAZIL_STOCKS)
    fiis = get_multiple(BRAZIL_FIIS)
    all_assets = stocks + fiis
    return pick_best(all_assets, score_dividend_asset)


def analyze_usa() -> Optional[Dict]:
    """Retorna a melhor dica do dia para os EUA."""
    stocks = get_multiple(US_STOCKS)
    reits = get_multiple(US_REITS)
    all_assets = stocks + reits
    return pick_best(all_assets, score_dividend_asset)


def analyze_europe() -> Optional[Dict]:
    """Retorna a melhor dica do dia para a Europa."""
    stocks = get_multiple(EUROPE_STOCKS)
    return pick_best(stocks, score_dividend_asset)


def analyze_crypto() -> Optional[Dict]:
    """Retorna a melhor oportunidade de cripto do momento."""
    cryptos = get_multiple(CRYPTO)
    best = pick_best(cryptos, score_crypto)
    # Só retorna se tiver momentum interessante
    if best and (best.get("change_pct") or 0) > 1.5:
        return best
    return None
