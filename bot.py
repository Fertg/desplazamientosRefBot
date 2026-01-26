import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler
)
from utils import generar_pdf

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CLAVE_ACCESO = os.getenv("ACCESO_CODE")

# Estados de la conversación
(AUTH, CATEGORIA_SELECCION, CAT_PDF, EQUIPO_A, EQUIPO_B, FECHA, TRAYECTO_DE, TRAYECTO_A, 
 KILOMETROS, VEHICULO_INFO, MATRICULA, LUGAR_FIRMA, APELLIDOS, NOMBRE, DNI, FIRMA, NUEVO_TRAMITE) = range(17)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Bienvenido. Introduce el código de acceso:")
    return AUTH

async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == CLAVE_ACCESO:
        # MENSAJE DE TRANQUILIDAD Y PRIVACIDAD
        aviso_privacidad = (
            "🛡️ *AVISO DE PRIVACIDAD*\n"
            "Este bot ha sido diseñado para procesar tus desplazamientos de forma efímera:\n\n"
            "1️⃣ *Sin Base de Datos:* No guardamos tu DNI, nombre ni firma.\n"
            "2️⃣ *Memoria Temporal:* Los datos solo residen en la memoria mientras rellenas el formulario.\n"
            "3️⃣ *Borrado Automático:* Al finalizar o cancelar, toda tu información se elimina por completo.\n\n"
            "✅ *Acceso concedido.*"
        )
        await update.message.reply_text(aviso_privacidad, parse_mode='Markdown')
        return await mostrar_menu_categorias(update)
    
    await update.message.reply_text("❌ Código incorrecto. Inténtalo de nuevo:")
    return AUTH

async def mostrar_menu_categorias(update):
    botones = [['AMISTOSO', 'DIP. BA', 'DIP. CC'], ['JUDEX', 'JUDEX CON DIETA', 'NACIONAL']]
    markup = ReplyKeyboardMarkup(botones, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("📋 Selecciona el tipo de PDF a generar:", reply_markup=markup)
    return CATEGORIA_SELECCION

async def get_categoria_seleccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['categoria_tipo'] = update.message.text
    await update.message.reply_text("📝 Categoría interna (Ej: 1ª Div. Nacional):", reply_markup=ReplyKeyboardRemove())
    return CAT_PDF

async def get_cat_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['categoria_pdf_texto'] = update.message.text
    await update.message.reply_text("🏠 Equipo LOCAL (Equipo A):")
    return EQUIPO_A

async def get_equipo_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['equipoA'] = update.message.text
    await update.message.reply_text("🚀 Equipo VISITANTE (Equipo B):")
    return EQUIPO_B

async def get_equipo_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['equipoB'] = update.message.text
    await update.message.reply_text("📅 Fecha del encuentro (DD.MM.AAAA):")
    return FECHA

async def get_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fecha'] = update.message.text
    await update.message.reply_text("📍 Población de SALIDA:")
    return TRAYECTO_DE

async def get_trayecto_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['de'] = update.message.text
    await update.message.reply_text("📍 Población de DESTINO:")
    return TRAYECTO_A

async def get_trayecto_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['a'] = update.message.text
    await update.message.reply_text("🚗 Kilómetros totales (ida y vuelta):")
    return KILOMETROS

async def get_kilometros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kms'] = update.message.text
    await update.message.reply_text("🚘 Vehículo (Marca y Modelo):")
    return VEHICULO_INFO

async def get_vehiculo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vehiculo'] = update.message.text
    await update.message.reply_text("🔢 Matrícula:")
    return MATRICULA

async def get_matricula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['matricula'] = update.message.text
    await update.message.reply_text("📍 Lugar de la firma (Población):")
    return LUGAR_FIRMA

async def get_lugar_firma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lugar_firma'] = update.message.text
    await update.message.reply_text("👤 Tus APELLIDOS:")
    return APELLIDOS

async def get_apellidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['apellidos'] = update.message.text
    await update.message.reply_text("👤 Tu NOMBRE:")
    return NOMBRE

async def get_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nombre'] = update.message.text
    context.user_data['nombre_completo'] = f"{update.message.text} {context.user_data['apellidos']}"
    await update.message.reply_text("💳 Número de D.N.I.:")
    return DNI

async def get_dni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dni'] = update.message.text
    await update.message.reply_text("✍️ Envíame una FOTO de tu firma:")
    return FIRMA

async def get_firma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    os.makedirs('firmas', exist_ok=True)
    path = f"firmas/firma_{update.message.from_user.id}.png"
    await photo_file.download_to_drive(path)
    context.user_data['firma_path'] = path
    
    await update.message.reply_text("⏳ Generando PDF y limpiando sesión...")
    ruta_pdf = generar_pdf(context.user_data)
    
    if ruta_pdf:
        with open(ruta_pdf, 'rb') as doc:
            await update.message.reply_document(document=doc, filename=os.path.basename(ruta_pdf))
        
        # Preguntar si quiere otro
        markup = ReplyKeyboardMarkup([['SÍ', 'NO']], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("✅ PDF enviado con éxito.\n¿Deseas generar otro desplazamiento?", reply_markup=markup)
        return NUEVO_TRAMITE
    else:
        await update.message.reply_text("❌ Error al generar el PDF.")
        context.user_data.clear()
        return ConversationHandler.END

async def gestionar_reinicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text.upper()
    # Limpiamos todos los datos SIEMPRE al llegar aquí para cumplir la promesa de privacidad
    context.user_data.clear()
    
    if respuesta == 'SÍ':
        return await mostrar_menu_categorias(update)
    else:
        await update.message.reply_text("👋 Sesión finalizada y datos borrados. ¡Hasta pronto!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # Limpiar al cancelar
    await update.message.reply_text("🚫 Proceso cancelado. Datos eliminados.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_auth)],
            CATEGORIA_SELECCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_categoria_seleccion)],
            CAT_PDF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cat_pdf)],
            EQUIPO_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_equipo_a)],
            EQUIPO_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_equipo_b)],
            FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fecha)],
            TRAYECTO_DE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trayecto_de)],
            TRAYECTO_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trayecto_a)],
            KILOMETROS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kilometros)],
            VEHICULO_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vehiculo)],
            MATRICULA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_matricula)],
            LUGAR_FIRMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lugar_firma)],
            APELLIDOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_apellidos)],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nombre)],
            DNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dni)],
            FIRMA: [MessageHandler(filters.PHOTO, get_firma)],
            NUEVO_TRAMITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, gestionar_reinicio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()