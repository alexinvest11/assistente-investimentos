import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Assistente de Investimentos",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📈 Assistente de Investimentos")
st.caption("Seu assistente pessoal • Uso exclusivo")

st.markdown("---")

# Carrega as últimas dicas
TIPS_FILE = Path("data/latest_tips.json")

def load_tips():
    if TIPS_FILE.exists():
        try:
            with open(TIPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

tips_data = load_tips()

if tips_data:
    updated = tips_data.get("updated_at", "")
    try:
        dt = datetime.fromisoformat(updated)
        st.success(f"Última atualização: {dt.strftime('%d/%m/%Y %H:%M')}")
    except:
        st.success("Dicas carregadas")
    
    tips = tips_data.get("tips", {})
    
    def show_tip(title, tip):
        st.subheader(title)
        if not tip:
            st.warning("Nenhuma dica disponível no momento.")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ticker", tip.get("ticker", "-"))
            st.write(f"**{tip.get('name', '')}**")
        with col2:
            price = tip.get("price")
            currency = tip.get("currency", "")
            st.metric("Preço", f"{currency} {price}")
            change = tip.get("change_pct")
            st.metric("Variação", f"{change}%" if change is not None else "-")
        
        dy = tip.get("dividend_yield")
        if dy:
            st.write(f"Dividend Yield: **{dy*100:.1f}%**")
        
        st.caption(f"Score interno: {tip.get('score', 'N/A')}")
        st.markdown("---")
    
    show_tip("🇧🇷 Brasil (Ações / FIIs)", tips.get("brazil"))
    show_tip("🇺🇸 EUA (Ações / REITs)", tips.get("usa"))
    show_tip("🇪🇺 Europa", tips.get("europe"))
    
    crypto_tip = tips.get("crypto")
    if crypto_tip:
        show_tip("₿ Criptomoedas (oportunidade)", crypto_tip)
    else:
        st.subheader("₿ Criptomoedas")
        st.info("Nenhuma oportunidade forte no momento. O sistema avisa no Telegram quando surgir algo interessante.")
else:
    st.info("Ainda não há análises geradas. As dicas aparecerão aqui após a primeira execução diária.")

st.markdown("---")
st.caption("Corretora prioritária para Brasil: **Rico**  \nIsto não é recomendação de investimento. Faça sua própria análise.")
