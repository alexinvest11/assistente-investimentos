"""
Job diário que gera as dicas, salva no repositório e envia avisos pelo Telegram.
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
HISTORY_FILE = DATA_DIR / "history.json"


def load_existing_tips() -> dict:
    if TIPS_FILE.exists():
        try:
            with open(TIPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"updated_at": None, "tips": {}}


def save_tips(payload: dict):
    with open(TIPS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

    # Histórico simples (mantém as últimas 30 entradas)
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tips": payload.get("tips", {})
    })
    history = history[-30:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2, default=str)


def format_tip(region: str, tip: dict) -> str:
    if not tip:
        return f"{region}: nenhuma dica encontrada hoje."

    dy = tip.get("dividend_yield")
    dy_str = f"{dy*100:.1f}%" if dy else "N/A"
    reason = tip.get("reason", "")

    text = (
        f"<b>{region}</b>\n"
        f"Ticker: <b>{tip['ticker']}</b>\n"
        f"Nome: {tip.get('name', '')}\n"
        f"Preço: {tip.get('currency', '')} {tip.get('price')}\n"
        f"Variação: {tip.get('change_pct')}%\n"
        f"Dividend Yield: {dy_str}\n\n"
        f"<b>Por que foi indicado:</b>\n{reason}"
    )
    return text


def run_analysis(regions: list = None):
    if regions is None:
        regions = ["brazil", "usa", "europe", "crypto"]

    existing = load_existing_tips()
    results = existing.get("tips", {}) or {}

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

    payload = {
        "updated_at": datetime.now().isoformat(),
        "tips": results
    }
    save_tips(payload)
    return results


if __name__ == "__main__":
    print("Iniciando análise diária...")
    run_analysis()
    print("Análise concluída.")
