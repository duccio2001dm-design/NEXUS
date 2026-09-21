import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from database import init_db, get_open_trades, get_trade_count, create_trade, close_trade


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 NEXUS online.\n\n"
        "Comandi:\n"
        "/stato - stato e trade aperte\n"
        "/trade BTC LONG 104500 103800 106000 - registra una trade\n"
        "/chiudi ID PREZZO - chiude una trade\n"
        "/analisi - prossimamente"
    )


async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open_trades = get_open_trades()
    total = get_trade_count()

    lines = [
        "🤖 NEXUS",
        "",
        f"📊 Trade registrate: {total}",
        f"🟢 Trade aperte: {len(open_trades)}",
    ]

    if open_trades:
        lines += ["", "Trade aperte:"]
        for trade in open_trades:
            lines.append(
                f"• #{trade['id']} {trade['symbol']} {trade['side']} @ {trade['entry']}"
            )

    await update.message.reply_text("\n".join(lines))


async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text(
            "Uso: /trade SIMBOLO LONG/SHORT ENTRY [SL] [TP]\n"
            "Esempio: /trade BTC LONG 104500 103800 106000"
        )
        return

    try:
        symbol = context.args[0].upper()
        side = context.args[1].upper()
        entry = float(context.args[2])
        stop_loss = float(context.args[3]) if len(context.args) > 3 else None
        take_profit = float(context.args[4]) if len(context.args) > 4 else None

        if side not in ("LONG", "SHORT"):
            raise ValueError("direzione")

        trade_id = create_trade(symbol, side, entry, stop_loss, take_profit)

        await update.message.reply_text(
            f"✅ Trade #{trade_id} registrata\n"
            f"📌 {symbol} {side}\n"
            f"Entry: {entry}\n"
            f"SL: {stop_loss if stop_loss is not None else '-'}\n"
            f"TP: {take_profit if take_profit is not None else '-'}"
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Formato non valido.\n"
            "Esempio: /trade BTC LONG 104500 103800 106000"
        )


async def chiudi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Uso: /chiudi ID PREZZO")
        return

    try:
        trade_id = int(context.args[0])
        exit_price = float(context.args[1])
        result = close_trade(trade_id, exit_price)

        if result is None:
            await update.message.reply_text("❌ Trade non trovata o già chiusa.")
            return

        await update.message.reply_text(
            f"🔒 Trade #{trade_id} chiusa\n"
            f"Prezzo uscita: {exit_price}\n"
            f"Risultato: {result:+.2f}"
        )
    except ValueError:
        await update.message.reply_text("❌ Usa: /chiudi ID PREZZO")


async def analisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 /analisi sarà il prossimo modulo.")


def main():
    init_db()

    public_url = os.getenv("NEXUS_PUBLIC_URL", "").rstrip("/")
    port = int(os.getenv("PORT", "8000"))
    webhook_path = os.getenv("NEXUS_WEBHOOK_PATH", "telegram")
    secret_token = os.getenv("NEXUS_WEBHOOK_SECRET", "")

    if not public_url:
        raise RuntimeError(
            "NEXUS_PUBLIC_URL is required when running NEXUS in webhook mode."
        )

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stato", stato))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("chiudi", chiudi))
    application.add_handler(CommandHandler("analisi", analisi))

    webhook_url = f"{public_url}/{webhook_path}"

    print(f"NEXUS webhook: {webhook_url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        secret_token=secret_token or None,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
