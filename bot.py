from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from database import init_db, get_open_trades, get_trade_count


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 NEXUS online.\n\n"
        "Comandi disponibili:\n"
        "/stato - stato del bot\n"
        "/trade - prossimamente\n"
        "/chiudi - prossimamente\n"
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
        lines.append("")
        lines.append("Trade aperte:")
        for trade in open_trades:
            lines.append(
                f"• #{trade['id']} {trade['symbol']} {trade['side']} @ {trade['entry']}"
            )

    await update.message.reply_text("\n".join(lines))


async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 /trade sarà il prossimo modulo. "
        "Per ora NEXUS sta preparando il database."
    )


async def chiudi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔒 /chiudi sarà disponibile quando avremo completato la gestione delle trade."
    )


async def analisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 /analisi sarà il modulo che studierà le tue operazioni."
    )


def main():
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stato", stato))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("chiudi", chiudi))
    application.add_handler(CommandHandler("analisi", analisi))

    print("NEXUS is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
