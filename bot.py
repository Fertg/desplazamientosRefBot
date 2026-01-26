import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
# Cargamos la clave desde el entorno. Si no existe, usamos una por defecto (opcional)
CLAVE_REAL = os.getenv("ACCESO_CODE") 

# Definimos los estados de la conversación
CODIGO, CATEGORIA, ENCUENTRO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Bienvenido. Introduce el código de acceso para continuar:")
    return CODIGO

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    # Comparamos con la variable de entorno
    if user_input == CLAVE_REAL:
        botones = [
            ['AMISTOSO', 'DIP. BA', 'DIP. CC'],
            ['JUDEX', 'JUDEX CON DIETA', 'NACIONAL']
        ]
        markup = ReplyKeyboardMarkup(botones, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "✅ Acceso concedido.\n\nSelecciona la **categoría del desplazamiento**:",
            reply_markup=markup
        )
        return CATEGORIA
    else:
        await update.message.reply_text("❌ Código incorrecto. Inténtalo de nuevo:")
        return CODIGO

# ... (el resto de funciones seleccionar_categoria y cancel se mantienen igual)

async def seleccionar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['categoria'] = update.message.text
    await update.message.reply_text(
        f"Has elegido: {update.message.text}\n\nAhora dime el **Nombre del Encuentro**:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ENCUENTRO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if not TOKEN or not CLAVE_REAL:
        print("ERROR: Falta el BOT_TOKEN o el ACCESO_CODE en las variables de entorno.")
        return

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, seleccionar_categoria)],
            ENCUENTRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: ConversationHandler.END)], 
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot en marcha y configurado con variables de entorno...")
    app.run_polling()

if __name__ == "__main__":
    main()