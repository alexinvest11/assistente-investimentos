"""
Coleta de dados de ações, FIIs e criptomoedas (Brasil) + notícias.
"""
import yfinance as yf
from typing import List, Dict, Optional


def normalize_dividend_yield(raw, ticker: str = "") -> Optional[float]:
    if raw is None:
        return None
    try:
        dy = float(raw)
    except (TypeError, ValueError):
        return None

    if dy > 1:
        dy = dy / 100

    # Brasil/FIIs podem ter DY mais altos; acima de 20% tratamos como erro
    if dy < 0 or dy > 0.20:
        return None
    return dy


def get_news(ticker: str, limit: int = 3) -> List[str]:
    """Busca manchetes recentes do ativo (quando disponível)."""
    headlines = []
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        for item in news[:limit]:
            # yfinance pode devolver formatos diferentes
            title = None
            if isinstance(item, dict):
                title = item.get("title") or item.get("content", {}).get("title")
                if not title and "content" in item and isinstance(item["content"], dict):
                    title = item["content"].get("title")
            if title:
                headlines.append(str(title).strip())
    except Exception as e:
        print(f"Erro ao buscar notícias de {ticker}: {e}")
    return headlines


def get_ticker_info(ticker: str, with_news: bool = True) -> Optional[Dict]:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1mo")

        if hist.empty:
            return None

        price = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else price
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0

        dy = normalize_dividend_yield(info.get("dividendYield"), ticker)
        news = get_news(ticker) if with_news else []

        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": round(float(price), 2),
            "change_pct": round(float(change_pct), 2),
            "currency": info.get("currency", "BRL"),
            "dividend_yield": dy,
            "pe_ratio": info.get("trailingPE"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "news": news,
        }
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return None


def get_multiple(tickers: List[str], with_news: bool = True) -> List[Dict]:
    results = []
    for t in tickers:
        data = get_ticker_info(t, with_news=with_news)
        if data:
            results.append(data)
    return results


BRAZIL_STOCKS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "WEGE3.SA",
    "ABEV3.SA", "BBAS3.SA", "RENT3.SA", "SUZB3.SA", "VIVT3.SA",
    "B3SA3.SA", "ELET3.SA", "PRIO3.SA", "EQTL3.SA", "RAIL3.SA",
]

BRAZIL_FIIS = [
    "HGLG11.SA", "XPLG11.SA", "MXRF11.SA", "KNRI11.SA", "BTLG11.SA",
    "HGRE11.SA", "VISC11.SA", "XPML11.SA", "KNCR11.SA", "TRXF11.SA",
    "HGBS11.SA", "BCFF11.SA", "IRDM11.SA", "CPTS11.SA", "TGAR11.SA",
]

CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
