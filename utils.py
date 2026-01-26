import io
import os
import re
import unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from coords import PDF_TEMPLATES

# ELIMINADA LA LÍNEA QUE CAUSABA EL ERROR (from utils import generar_pdf)

def limpiar_texto(texto):
    """Elimina tildes y convierte espacios en guiones bajos."""
    if not texto: return "info"
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9]+', '_', texto)
    return texto.upper()

def generar_pdf(datos):
    categoria = datos.get('categoria', 'NACIONAL')
    template = PDF_TEMPLATES.get(categoria)
    
    if not template:
        print(f"Error: No hay plantilla para la categoría {categoria}")
        return None

    # 1. Crear el overlay en memoria
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    can.setFont("Helvetica", 10)
    # Escribir los datos usando las coordenadas de coords.py
    can.drawString(template['encuentro'][0], template['encuentro'][1], datos.get('encuentro', ''))
    can.drawString(template['fecha'][0], template['fecha'][1], datos.get('fecha', ''))
    can.drawString(template['trayecto_de'][0], template['trayecto_de'][1], datos.get('de', ''))
    can.drawString(template['trayecto_a'][0], template['trayecto_a'][1], datos.get('a', ''))
    can.drawString(template['kms'][0], template['kms'][1], datos.get('kms', ''))
    can.drawString(template['vehiculo'][0], template['vehiculo'][1], datos.get('vehiculo', ''))
    can.drawString(template['matricula'][0], template['matricula'][1], datos.get('matricula', ''))
    can.drawString(template['fdo_nombre'][0], template['fdo_nombre'][1], datos.get('nombre_completo', ''))
    can.drawString(template['dni'][0], template['dni'][1], datos.get('dni', ''))

    # Insertar la firma
    if 'firma_path' in datos:
        can.drawImage(datos['firma_path'], template['firma'][0], template['firma'][1], width=100, preserveAspectRatio=True, mask='auto')

    can.save()
    packet.seek(0)

    # 2. Fusionar con el PDF base
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open(template['base'], "rb"))
    output = PdfWriter()

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # 3. Formatear nombre del archivo: NACIONAL_2025.10.20_APELLIDO_NOMBRE.pdf
    fecha_raw = datos.get('fecha', '00.00.00')
    fecha_formateada = fecha_raw.replace("/", ".").replace("-", ".")
    nombre_arbitro = limpiar_texto(datos.get('nombre_completo', 'USUARIO'))
    
    nombre_archivo_final = f"{categoria}_{fecha_formateada}_{nombre_arbitro}.pdf"
    
    if not os.path.exists('output'): 
        os.makedirs('output')
    
    ruta_salida = os.path.join('output', nombre_archivo_final)
    
    with open(ruta_salida, "wb") as outputStream:
        output.write(outputStream)
    
    return ruta_salida