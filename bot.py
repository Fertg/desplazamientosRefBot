import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

load_dotenv()  # 👈 ESTO ES LO QUE FALTABA

TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Hola! Introduce el código de acceso.")

def main():
    print("TOKEN =", TOKEN)  # 👈 solo para comprobar
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
