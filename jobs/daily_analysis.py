"""
Job diário que gera as dicas e envia avisos pelo Telegram.
Pode ser executado manualmente ou via GitHub Actions / cron.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from core.analyzers import analyze_brazil, analyze_usa, analyze_europe, analyze_crypto
from core.notifications import enviar_aviso

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TIPS_FILE = DATA_DIR / "latest_tips.json"


def format_tip(region: str, tip: dict) -> str:
    if not tip:
        return f"{region}: nenhuma dica encontrada hoje."
    
    dy = tip.get("dividend_yield")
    dy_str = f"{dy*100:.1f}%" if dy else "N/A"
    
    text = (
        f"<b>{region}</b>\n"
        f"Ticker: <b>{tip['ticker']}</b>\n"
        f"Nome: {tip.get('name', '')}\n"
        f"Preço: {tip.get('currency', '')} {tip.get('price')}\n"
        f"Variação: {tip.get('change_pct')}%\n"
        f"Dividend Yield: {dy_str}\n"
        f"Score: {tip.get('score', 'N/A')}"
    )
    return text


def run_analysis(regions: list = None):
    """
    Executa a análise das regiões solicitadas e envia avisos.
    regions pode ser: ['brazil'], ['usa'], ['europe'], ['crypto'] ou None (todas).
    """
    if regions is None:
        regions = ["brazil", "usa", "europe", "crypto"]
    
    results = {}
    
    if "brazil" in regions:
        tip = analyze_brazil()
        results["brazil"] = tip
        msg = "✅ <b>Nova dica Brasil pronta</b>\n\n" + format_tip("Brasil", tip)
        enviar_aviso(msg)
        print("Dica Brasil enviada")
    
    if "usa" in regions:
        tip = analyze_usa()
        results["usa"] = tip
        msg = "✅ <b>Nova dica EUA pronta</b>\n\n" + format_tip("EUA", tip)
        enviar_aviso(msg)
        print("Dica EUA enviada")
    
    if "europe" in regions:
        tip = analyze_europe()
        results["europe"] = tip
        msg = "✅ <b>Nova dica Europa pronta</b>\n\n" + format_tip("Europa", tip)
        enviar_aviso(msg)
        print("Dica Europa enviada")
    
    if "crypto" in regions:
        tip = analyze_crypto()
        results["crypto"] = tip
        if tip:
            msg = "🚨 <b>Alerta Cripto</b>\n\n" + format_tip("Cripto", tip)
            enviar_aviso(msg)
            print("Alerta Cripto enviado")
        else:
            print("Nenhuma oportunidade interessante de cripto no momento")
    
    # Salva o resultado para o aplicativo mostrar
    payload = {
        "updated_at": datetime.now().isoformat(),
        "tips": results
    }
    with open(TIPS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    
    return results


if __name__ == "__main__":
    print("Iniciando análise diária...")
    run_analysis()
    print("Análise concluída.")
