"""
Coleta de dados de ações, FIIs/REITs e criptomoedas usando yfinance.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def get_ticker_info(ticker: str) -> Optional[Dict]:
    """Retorna informações básicas de um ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1mo")
        
        if hist.empty:
            return None
            
        price = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else price
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
        
        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": round(float(price), 2),
            "change_pct": round(float(change_pct), 2),
            "currency": info.get("currency", "USD"),
            "dividend_yield": info.get("dividendYield"),
            "pe_ratio": info.get("trailingPE"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
        }
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return None


def get_multiple(tickers: List[str]) -> List[Dict]:
    """Busca vários tickers e retorna apenas os que funcionaram."""
    results = []
    for t in tickers:
        data = get_ticker_info(t)
        if data:
            results.append(data)
    return results


# Listas iniciais de ativos para análise
BRAZIL_STOCKS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "WEGE3.SA", 
                 "ABEV3.SA", "BBAS3.SA", "RENT3.SA", "SUZB3.SA", "VIVT3.SA"]

BRAZIL_FIIS = ["HGLG11.SA", "XPLG11.SA", "MXRF11.SA", "KNRI11.SA", "BTLG11.SA",
               "HGRE11.SA", "VISC11.SA", "XPML11.SA", "KNCR11.SA", "TRXF11.SA"]

US_STOCKS = ["AAPL", "MSFT", "JNJ", "PG", "KO", "PEP", "V", "MA", "JPM", "UNH"]
US_REITS = ["O", "AMT", "PLD", "SPG", "CCI", "EQIX", "DLR", "PSA", "WELL", "AVB"]

EUROPE_STOCKS = ["NESN.SW", "ASML.AS", "SAP.DE", "SIE.DE", "OR.PA", 
                 "MC.PA", "SAN.MC", "BBVA.MC", "ENEL.MI", "IBE.MC"]

CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
