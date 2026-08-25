import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Assistente de Investimentos",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Assistente de Investimentos")
st.write("Versão inicial do seu aplicativo pessoal")

st.markdown("---")

st.subheader("Status")
st.success("Aplicativo funcionando!")

st.write(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.markdown("---")
st.info("Em breve: dicas diárias de Brasil, EUA, Europa e alertas de criptomoedas.")
