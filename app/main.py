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
st.caption("Brasil • Ações, FIIs e Criptomoedas • Uso pessoal")

TIPS_FILE = Path("data/latest_tips.json")


def load_tips():
    if TIPS_FILE.exists():
        try:
            with open(TIPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def show_tip(tip):
    if not tip:
        st.warning("Nenhuma dica disponível no momento.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Código", tip.get("ticker", "-"))
        st.write(f"**{tip.get('name', '')}**")
    with col2:
        price = tip.get("price")
        currency = tip.get("currency", "")
        st.metric("Preço", f"{currency} {price}")
        change = tip.get("change_pct")
        st.metric("Variação", f"{change}%" if change is not None else "-")

    dy = tip.get("dividend_yield")
    if dy and tip.get("kind") != "crypto":
        st.write(f"Proventos (aprox.): **{dy*100:.1f}% ao ano**")

    reason = tip.get("reason")
    if reason:
        st.info(f"**Por que foi indicado:**  \n{reason}")

    news = tip.get("news") or []
    if news:
        with st.expander("Notícias recentes relacionadas"):
            for n in news[:3]:
                st.write(f"• {n}")


tips_data = load_tips()

if tips_data:
    updated = tips_data.get("updated_at", "")
    try:
        dt = datetime.fromisoformat(updated)
        st.success(f"Última atualização: {dt.strftime('%d/%m/%Y %H:%M')}")
    except Exception:
        st.success("Dicas carregadas")

    tips = tips_data.get("tips", {})

    tab1, tab2, tab3 = st.tabs(["📈 Ações", "🏢 Fundos Imobiliários", "₿ Criptomoedas"])

    with tab1:
        st.subheader("Dica de ações (Brasil)")
        show_tip(tips.get("stocks"))

    with tab2:
        st.subheader("Dica de fundos imobiliários (FIIs)")
        show_tip(tips.get("fiis"))

    with tab3:
        st.subheader("Dica de criptomoedas")
        crypto_tip = tips.get("crypto")
        if crypto_tip:
            show_tip(crypto_tip)
        else:
            st.info(
                "Nenhuma oportunidade forte no momento. "
                "O sistema avisa no Telegram quando surgir algo interessante."
            )
else:
    st.info("Ainda não há análises gravadas. As dicas aparecerão após as próximas execuções.")

st.markdown("---")
st.caption(
    "Corretora prioritária: **Rico**  \n"
    "Isto não é recomendação de investimento. Faça sua própria análise."
)
