import io
import os
import re
import unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from coords import PDF_TEMPLATES

def limpiar_texto(texto):
    """Limpia el texto para nombres de archivo seguros."""
    if not texto: return "INFO"
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9]+', '_', texto)
    return texto.upper()

def generar_pdf(datos):
    categoria_key = datos.get('categoria_tipo', 'NACIONAL')
    template = PDF_TEMPLATES.get(categoria_key)
    
    if not template: 
        print(f"Error: No se encontró la plantilla {categoria_key}")
        return None

    # Configuración de rutas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_pdf_base = os.path.join(base_dir, template['base'])

    if not os.path.exists(ruta_pdf_base):
        print(f"Error: El archivo base no existe en {ruta_pdf_base}")
        return None

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # --- INICIO REJILLA DE GUÍA (Borrar o comentar cuando termines de ajustar) ---
    can.setFont("Helvetica", 7)
    can.setStrokeColorRGB(0.8, 0.8, 0.8)  # Color gris claro para las líneas
    for x in range(0, 601, 50):
        can.line(x, 0, x, 850)
        can.drawString(x + 2, 10, str(x))  # Números en el eje X
    for y in range(0, 851, 50):
        can.line(0, y, 600, y)
        can.drawString(10, y + 2, str(y))  # Números en el eje Y
    # --- FIN REJILLA DE GUÍA ---

    can.setFont("Helvetica", 10)
    can.setFillColorRGB(0, 0, 0) # Asegurar color negro para el texto

    # Dibujar datos usando coordenadas de coords.py
    # Nota: Asegúrate de que 'categoria_encuentro' existe en tu coords.py
    if 'categoria_encuentro' in template:
        can.drawString(template['categoria_encuentro'][0], template['categoria_encuentro'][1], datos.get('categoria_pdf_texto', ''))
    
    can.drawString(template['encuentro'][0], template['encuentro'][1], datos.get('encuentro', ''))
    can.drawString(template['fecha'][0], template['fecha'][1], datos.get('fecha', ''))
    can.drawString(template['trayecto_de'][0], template['trayecto_de'][1], datos.get('de', ''))
    can.drawString(template['trayecto_a'][0], template['trayecto_a'][1], datos.get('a', ''))
    can.drawString(template['kms'][0], template['kms'][1], datos.get('kms', ''))
    can.drawString(template['vehiculo'][0], template['vehiculo'][1], datos.get('vehiculo', ''))
    can.drawString(template['matricula'][0], template['matricula'][1], datos.get('matricula', ''))
    can.drawString(template['fdo_nombre'][0], template['fdo_nombre'][1], datos.get('nombre_completo', ''))
    can.drawString(template['dni'][0], template['dni'][1], datos.get('dni', ''))

    # Insertar firma
    if 'firma_path' in datos and os.path.exists(datos['firma_path']):
        can.drawImage(datos['firma_path'], template['firma'][0], template['firma'][1], width=100, preserveAspectRatio=True, mask='auto')

    can.save()
    packet.seek(0)

    # Fusionar con el PDF original
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open(ruta_pdf_base, "rb"))
    output = PdfWriter()
    
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Nombre del archivo: CATEGORIA_FECHA_APELLIDOS_NOMBRE.pdf
    fecha_f = datos.get('fecha', '00.00.00').replace("/", ".").replace("-", ".")
    apellidos_f = limpiar_texto(datos.get('apellidos', 'APELLIDO'))
    nombre_f = limpiar_texto(datos.get('nombre', 'NOMBRE'))
    
    nombre_archivo = f"{categoria_key}_{fecha_f}_{apellidos_f}_{nombre_f}.pdf"
    
    os.makedirs('output', exist_ok=True)
    ruta_salida = os.path.join('output', nombre_archivo)
    
    with open(ruta_salida, "wb") as f:
        output.write(f)
    
    return ruta_salida