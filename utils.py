import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from utils import generar_pdf  # Importamos tu función de utils.py

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CLAVE_ACCESO = os.getenv("ACCESO_CODE")

# Definición de estados de la conversación
(AUTH, CATEGORIA, ENCUENTRO, FECHA, TRAYECTO_DE, TRAYECTO_A, 
 KILOMETROS, VEHICULO_INFO, MATRICULA, NOMBRE_APELLIDOS, DNI, FIRMA) = range(12)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Punto de inicio: Pide el código de acceso"""
    await update.message.reply_text("🔐 Bienvenido. Introduce el código de acceso para continuar:")
    return AUTH

async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica la clave desde la variable de entorno"""
    if update.message.text == CLAVE_ACCESO:
        botones = [
            ['AMISTOSO', 'DIP. BA', 'DIP. CC'],
            ['JUDEX', 'JUDEX CON DIETA', 'NACIONAL']
        ]
        markup = ReplyKeyboardMarkup(botones, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("✅ Acceso correcto. Selecciona la categoría:", reply_markup=markup)
        return CATEGORIA
    else:
        await update.message.reply_text("❌ Código incorrecto. Inténtalo de nuevo:")
        return AUTH

async def get_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['categoria'] = update.message.text
    await update.message.reply_text("📝 Introduce el Encuentro (Ej: Equipo A vs Equipo B):", reply_markup=ReplyKeyboardRemove())
    return ENCUENTRO

async def get_encuentro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['encuentro'] = update.message.text
    await update.message.reply_text("📅 Introduce la Fecha del encuentro (Formato: DD.MM.AAAA):")
    return FECHA

async def get_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fecha'] = update.message.text
    await update.message.reply_text("📍 Trayecto Recorrido: ¿Desde qué población sales?")
    return TRAYECTO_DE

async def get_trayecto_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['de'] = update.message.text
    await update.message.reply_text("📍 ¿A qué población te desplazaste?")
    return TRAYECTO_A

async def get_trayecto_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['a'] = update.message.text
    await update.message.reply_text("🚗 ¿Cuántos Kilómetros totales hiciste (ida y vuelta)?")
    return KILOMETROS

async def get_kilometros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kms'] = update.message.text
    await update.message.reply_text("🚘 Datos del vehículo: Indica MARCA Y MODELO:")
    return VEHICULO_INFO

async def get_vehiculo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vehiculo'] = update.message.text
    await update.message.reply_text("🔢 Indica la MATRÍCULA del vehículo:")
    return MATRICULA

async def get_matricula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['matricula'] = update.message.text
    await update.message.reply_text("👤 Introduce tu Nombre y Apellidos (Para el nombre del archivo y Fdo):")
    return NOMBRE_APELLIDOS

async def get_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nombre_completo'] = update.message.text
    await update.message.reply_text("💳 Introduce tu número de D.N.I.:")
    return DNI

async def get_dni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dni'] = update.message.text
    await update.message.reply_text("✍️ Por último, envíame una FOTO de tu firma:")
    return FIRMA

async def get_firma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Descarga la firma, genera el PDF y lo envía"""
    # Descargar la imagen de la firma
    photo_file = await update.message.photo[-1].get_file()
    if not os.path.exists('firmas'):
        os.makedirs('firmas')
    
    path = f"firmas/firma_{update.message.from_user.id}.png"
    await photo_file.download_to_drive(path)
    context.user_data['firma_path'] = path
    
    await update.message.reply_text("⏳ Generando tu documento...")

    # Generar el PDF usando la función de utils.py
    try:
        ruta_pdf = generar_pdf(context.user_data)
        
        if ruta_pdf and os.path.exists(ruta_pdf):
            # Enviar el archivo generado al usuario
            with open(ruta_pdf, 'rb') as document:
                await update.message.reply_document(
                    document=document,
                    filename=os.path.basename(ruta_pdf),
                    caption="✅ Recibo generado con éxito."
                )
        else:
            await update.message.reply_text("❌ Error: No se pudo generar el archivo.")
    except Exception as e:
        print(f"Error generando PDF: {e}")
        await update.message.reply_text("❌ Ocurrió un error inesperado al generar el PDF.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación actual"""
    await update.message.reply_text("🚫 Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if not TOKEN or not CLAVE_ACCESO:
        print("CRITICAL ERROR: BOT_TOKEN o ACCESO_CODE no encontrados en el entorno.")
        return

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_auth)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_categoria)],
            ENCUENTRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_encuentro)],
            FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fecha)],
            TRAYECTO_DE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trayecto_de)],
            TRAYECTO_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trayecto_a)],
            KILOMETROS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kilometros)],
            VEHICULO_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vehiculo)],
            MATRICULA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_matricula)],
            NOMBRE_APELLIDOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nombre)],
            DNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dni)],
            FIRMA: [MessageHandler(filters.PHOTO, get_firma)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    
    print("Bot en marcha (Python 3.11 compatible)...")
    app.run_polling()

if __name__ == "__main__":
    main()