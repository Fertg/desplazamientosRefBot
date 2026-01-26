import io
import os
import re
import unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from coords import PDF_TEMPLATES

def limpiar_texto(texto):
    if not texto: return "INFO"
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9]+', '_', texto)
    return texto.upper()

def generar_pdf(datos):
    categoria_key = datos.get('categoria_tipo', 'NACIONAL')
    template = PDF_TEMPLATES.get(categoria_key)
    if not template: return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_pdf_base = os.path.join(base_dir, template['base'])

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    

    can.setFont("Helvetica", 10)
    can.setFillColorRGB(0, 0, 0)

    # 1. Equipos y Categoría
    can.drawString(template['categoria_encuentro'][0], template['categoria_encuentro'][1], datos.get('categoria_pdf_texto', ''))
    can.drawString(template['equipoA'][0], template['equipoA'][1], datos.get('equipoA', ''))
    can.drawString(template['equipoB'][0], template['equipoB'][1], datos.get('equipoB', ''))

    # 2. Fecha y Lugar desglosado
    fecha_raw = datos.get('fecha', '00.00.0000')
    can.drawString(template['fecha'][0], template['fecha'][1], fecha_raw)
    
    fecha_partes = fecha_raw.replace('/', '.').replace('-', '.').split('.')
    if len(fecha_partes) == 3:
        dia, mes_num, anio = fecha_partes
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        try:
            mes_texto = meses[int(mes_num)-1]
        except:
            mes_texto = mes_num
        
        # El lugar se dibuja basándose en la posición del día (movido a la izquierda)
        can.drawString(template['lugar_fecha_dia'][0] - 120, template['lugar_fecha_dia'][1], datos.get('lugar_firma', ''))
        can.drawString(template['lugar_fecha_dia'][0], template['lugar_fecha_dia'][1], dia)
        can.drawString(template['lugar_fecha_mes'][0], template['lugar_fecha_mes'][1], mes_texto)
        can.drawString(template['lugar_fecha_anio'][0], template['lugar_fecha_anio'][1], anio[-1])

    # 3. Resto de campos
    can.drawString(template['trayecto_de'][0], template['trayecto_de'][1], datos.get('de', ''))
    can.drawString(template['trayecto_a'][0], template['trayecto_a'][1], datos.get('a', ''))
    can.drawString(template['kms'][0], template['kms'][1], datos.get('kms', ''))
    can.drawString(template['vehiculo'][0], template['vehiculo'][1], datos.get('vehiculo', ''))
    can.drawString(template['matricula'][0], template['matricula'][1], datos.get('matricula', ''))
    can.drawString(template['fdo_nombre'][0], template['fdo_nombre'][1], datos.get('nombre_completo', ''))
    can.drawString(template['dni'][0], template['dni'][1], datos.get('dni', ''))

    # 4. Firma
    if 'firma_path' in datos and os.path.exists(datos['firma_path']):
        can.drawImage(datos['firma_path'], template['firma'][0], template['firma'][1], width=90, preserveAspectRatio=True, mask='auto')

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open(ruta_pdf_base, "rb"))
    output = PdfWriter()
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Formato de nombre solicitado
    fecha_slug = fecha_raw.replace("/", ".").replace("-", ".")
    nombre_archivo = f"{categoria_key}_{fecha_slug}_{limpiar_texto(datos.get('apellidos'))}_{limpiar_texto(datos.get('nombre'))}_Firmado.pdf"
    
    os.makedirs('output', exist_ok=True)
    ruta_salida = os.path.join('output', nombre_archivo)
    with open(ruta_salida, "wb") as f:
        output.write(f)
    return ruta_salida