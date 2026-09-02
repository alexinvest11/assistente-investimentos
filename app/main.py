import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Assistente de Investimentos",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📈 Assistente de Investimentos")
st.caption("Seu assistente pessoal de análises")

st.markdown("---")

st.subheader("Status do sistema")
st.success("Aplicativo online e funcionando!")

st.write(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.markdown("---")

st.subheader("Próximas funcionalidades")
st.info("""
**Em breve:**
- Dica diária Brasil (1h antes da abertura)
- Dica diária EUA
- Dica diária Europa
- Alertas de criptomoedas quando houver oportunidade
- Sugestão de corretora (Rico prioritária para Brasil)
""")

st.markdown("---")
st.caption("Uso pessoal • Não é recomendação de investimento")
