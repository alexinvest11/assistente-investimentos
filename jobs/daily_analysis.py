"""
Gera dicas de Ações, FIIs e Cripto, grava no app e avisa no Telegram.
"""
import json
from datetime import datetime
from pathlib import Path

from core.analyzers import analyze_stocks, analyze_fiis, analyze_crypto
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
    history = history[-40:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2, default=str)


def format_tip(categoria: str, tip: dict) -> str:
    if not tip:
        return f"{categoria}: nenhuma dica no momento."

    dy = tip.get("dividend_yield")
    dy_str = f"{dy*100:.1f}% ao ano" if dy else "não disponível"
    reason = tip.get("reason", "")

    text = (
        f"<b>{categoria}</b>\n"
        f"Código: <b>{tip['ticker']}</b>\n"
        f"Nome: {tip.get('name', '')}\n"
        f"Preço atual: {tip.get('currency', '')} {tip.get('price')}\n"
        f"Variação recente: {tip.get('change_pct')}%\n"
    )
    if tip.get("kind") != "crypto":
        text += f"Proventos (aprox.): {dy_str}\n"
    text += f"\n<b>Por que foi indicado:</b>\n{reason}"
    return text


def run_analysis(categories: list = None):
    """
    categories: ['stocks'], ['fiis'], ['crypto'] ou None (todos).
    """
    if categories is None:
        categories = ["stocks", "fiis", "crypto"]

    existing = load_existing_tips()
    results = existing.get("tips", {}) or {}

    # Remove dicas antigas de EUA/Europa se existirem
    results.pop("usa", None)
    results.pop("europe", None)
    results.pop("brazil", None)

    if "stocks" in categories:
        tip = analyze_stocks()
        results["stocks"] = tip
        msg = "✅ <b>Nova dica — Ações</b>\n\n" + format_tip("Ações (Brasil)", tip)
        enviar_aviso(msg)
        print("Dica Ações enviada")

    if "fiis" in categories:
        tip = analyze_fiis()
        results["fiis"] = tip
        msg = "✅ <b>Nova dica — Fundos Imobiliários</b>\n\n" + format_tip("FIIs", tip)
        enviar_aviso(msg)
        print("Dica FIIs enviada")

    if "crypto" in categories:
        tip = analyze_crypto()
        results["crypto"] = tip
        if tip:
            msg = "🚨 <b>Alerta Cripto</b>\n\n" + format_tip("Criptomoedas", tip)
            enviar_aviso(msg)
            print("Alerta Cripto enviado")
        else:
            print("Nenhuma oportunidade forte de cripto no momento")

    payload = {
        "updated_at": datetime.now().isoformat(),
        "tips": results
    }
    save_tips(payload)
    return results


if __name__ == "__main__":
    print("Iniciando análise...")
    run_analysis()
    print("Análise concluída.")
