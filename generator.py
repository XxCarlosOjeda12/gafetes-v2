#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo core para la generación de gafetes PDF.
"""

import os
import io
import logging
from typing import Dict, List, Optional, Tuple
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

try:
    from utils import sanitizar_nombre_archivo
except ImportError:
    import re
    def sanitizar_nombre_archivo(texto: str) -> str:
        """Elimina caracteres no válidos para nombres de archivo"""
        texto = re.sub(r'[^\w\s-]', '', texto.strip())
        texto = re.sub(r'[-\s]+', '_', texto)
        return texto or "sin_nombre"

logger = logging.getLogger(__name__)

ANCHO_PAGINA = 281 * mm   
ALTO_PAGINA = 453 * mm   
TAMANO_PAGINA_PERSONALIZADO = (ANCHO_PAGINA, ALTO_PAGINA)

ANCHO_PUNTOS = 796.5
ALTO_PUNTOS = 1283.5


AREA_NOMBRE_APELLIDO = {
    "x_centro": ANCHO_PUNTOS / 2,     
    "y_nombre": 880,                    
    "y_apellido": 800,                  
    "tamaño_fuente": 65
}

AREA_PUESTO = {
    "x_centro": (ANCHO_PUNTOS / 2) + 80,  
    "y_centro": 630,                     
    "tamaño_fuente": 32
}

AREA_OFICINA = {
    "x": 100,                            
    "y_centro": 700,                     
    "tamaño_fuente": 70
}

AREA_QR = {
    "x": 600,                            
    "y": 930,                            
    "tamaño": 150
}

POS = {
    "frente": {
        "nombre": (AREA_NOMBRE_APELLIDO["x_centro"], AREA_NOMBRE_APELLIDO["y_nombre"], AREA_NOMBRE_APELLIDO["tamaño_fuente"]),
        "apellido": (AREA_NOMBRE_APELLIDO["x_centro"], AREA_NOMBRE_APELLIDO["y_apellido"], AREA_NOMBRE_APELLIDO["tamaño_fuente"]),
        "puesto": (AREA_PUESTO["x_centro"], AREA_PUESTO["y_centro"], AREA_PUESTO["tamaño_fuente"]),
        "oficina": (AREA_OFICINA["x"], AREA_OFICINA["y_centro"], AREA_OFICINA["tamaño_fuente"]),
        "qr_1": (AREA_QR["x"], AREA_QR["y"], AREA_QR["tamaño"]),
    },
    "reverso": {
        "mesa": (315, 1121, 22),     
        "paseo": (150, 1055, 22),
    }
}

FONT_PATH = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/arialbd.ttf"  

MESAS_VALIDAS = [
    "Valuación",
    "Grúas", 
    "Q Salud",
    "Proyectos estratégicos",
    "Productos y Tarifas",
    "Verificaciones",
]

PASEOS_VALIDOS = [
    "Por el Centro Histórico",
    "Museando Ando",
    "Vamos Pa'l Mercado",
    "Colores de México"
]


def obtener_dimensiones_pdf(archivo_pdf: str) -> Tuple[float, float]:
    """Obtiene las dimensiones reales de un archivo PDF."""
    try:
        reader = PdfReader(archivo_pdf)
        page = reader.pages[0]
        mediabox = page.mediabox
        ancho = float(mediabox.width)
        alto = float(mediabox.height)
        logger.debug(f"Dimensiones detectadas del PDF {archivo_pdf}: {ancho:.1f} x {alto:.1f} puntos")
        return ancho, alto
    except Exception as e:
        logger.error(f"Error obteniendo dimensiones del PDF: {e}")
        return ANCHO_PUNTOS, ALTO_PUNTOS


def registrar_fuentes():
    """Registra las fuentes Arial normal y bold para Windows."""
    font_normal = 'Helvetica-Bold'
    font_bold = 'Helvetica-Bold'
    
    try:
        if os.path.exists(FONT_PATH):
            pdfmetrics.registerFont(TTFont('ArialFont', FONT_PATH))
            font_normal = 'ArialFont'
            logger.debug("Fuente Arial registrada correctamente")
        
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont('ArialBold', FONT_BOLD_PATH))
            font_bold = 'ArialBold'
            logger.debug("Fuente Arial Bold registrada correctamente")
        else:
            font_bold = 'Helvetica-Bold' 
            
    except Exception as e:
        logger.warning(f"Error registrando fuentes: {e}, usando Helvetica")
    
    return font_normal, font_bold


def validar_coordenadas(x: float, y: float, pagesize: tuple = None) -> tuple:
    """Valida y ajusta las coordenadas para que estén dentro de los límites."""
    if pagesize is None:
        pagesize = (ANCHO_PUNTOS, ALTO_PUNTOS)
    
    max_x, max_y = pagesize
    
    if x < 0:
        x = 10
    elif x > max_x:
        x = max_x - 10
    
    if y < 0:
        y = 10
    elif y > max_y:
        y = max_y - 10
    
    return x, y


def calcular_x_centrado(pdf_canvas: canvas.Canvas, texto: str, x_centro: float, 
                        font_name: str, font_size: float) -> float:
    """
    Calcula la posición X para centrar un texto horizontalmente.
    
    Args:
        pdf_canvas: Canvas de ReportLab
        texto: Texto a centrar
        x_centro: Posición X del centro deseado
        font_name: Nombre de la fuente
        font_size: Tamaño de la fuente
        
    Returns:
        Posición X ajustada para que el texto quede centrado
    """
    pdf_canvas.setFont(font_name, font_size)
    ancho_texto = pdf_canvas.stringWidth(texto, font_name, font_size)
    x_inicial = x_centro - (ancho_texto / 2)
    return x_inicial


def calcular_y_centrado_vertical(pdf_canvas: canvas.Canvas, texto: str, y_centro: float,
                                  font_name: str, font_size: float) -> float:
    """
    Calcula la posición Y para centrar un texto verticalmente (usado para texto rotado).
    
    Args:
        pdf_canvas: Canvas de ReportLab
        texto: Texto a centrar
        y_centro: Posición Y del centro deseado
        font_name: Nombre de la fuente
        font_size: Tamaño de la fuente
        
    Returns:
        Posición Y ajustada para que el texto quede centrado verticalmente
    """
    pdf_canvas.setFont(font_name, font_size)
    ancho_texto = pdf_canvas.stringWidth(texto, font_name, font_size)   
    y_inicial = y_centro - (ancho_texto / 2)
    return y_inicial


# def formatear_puesto(puesto: str) -> str:
#     """
#     Formatea el puesto con primera letra mayúscula, resto minúsculas.
#     Maneja casos especiales como 'de', 'y', etc.
#     """
#     if not puesto:
#         return ""
#     
#     # Palabras que deben quedar en minúsculas (excepto al inicio)
#     palabras_minusculas = {'de', 'del', 'la', 'las', 'los', 'y', 'e', 'o', 'u'}
#     
#     palabras = puesto.split()
#     resultado = []
#     
#     for i, palabra in enumerate(palabras):
#         if i == 0:  # Primera palabra siempre capitalizada
#             resultado.append(palabra.capitalize())
#         elif palabra.lower() in palabras_minusculas:
#             resultado.append(palabra.lower())
#         else:
#             resultado.append(palabra.capitalize())
#     
#     return ' '.join(resultado)


def agregar_contenido_frente(pdf_canvas: canvas.Canvas, nombre: str, apellido: str, 
                            oficina: str, puesto: str, qr_image: Optional[io.BytesIO] = None,
                            font_name: str = 'Helvetica-Bold'):
    """
    Agrega el contenido al frente del gafete - FORMATO INDIVIDUAL/NORMAL CON CENTRADO
    Nombre, apellido y oficina en BLANCO (centrados)
    Puesto en NEGRO (centrado, tal cual viene del Excel, sin transformaciones)
    """
    
    pagesize = pdf_canvas._pagesize if hasattr(pdf_canvas, '_pagesize') else (ANCHO_PUNTOS, ALTO_PUNTOS)
    pos = POS["frente"]
    
     
    pdf_canvas.setFillColorRGB(1, 1, 1)  
    
    x_centro, y, font_size = pos["nombre"]
    pdf_canvas.setFont(font_name, font_size)
    x_centrado = calcular_x_centrado(pdf_canvas, nombre, x_centro, font_name, font_size)
    x_val, y_val = validar_coordenadas(x_centrado, y, pagesize)
    pdf_canvas.drawString(x_val, y_val, nombre)
    
    x_centro, y, font_size = pos["apellido"]
    pdf_canvas.setFont(font_name, font_size)
    x_centrado = calcular_x_centrado(pdf_canvas, apellido, x_centro, font_name, font_size)
    x_val, y_val = validar_coordenadas(x_centrado, y, pagesize)
    pdf_canvas.drawString(x_val, y_val, apellido)
    
    puesto_texto = puesto[:50] if puesto else ""
    x_centro, y, font_size = pos["puesto"]
    pdf_canvas.setFillColorRGB(0, 0, 0) 
    pdf_canvas.setFont(font_name, font_size)
    x_centrado = calcular_x_centrado(pdf_canvas, puesto_texto, x_centro, font_name, font_size)
    x_val, y_val = validar_coordenadas(x_centrado, y, pagesize)
    pdf_canvas.drawString(x_val, y_val, puesto_texto)
    
    if qr_image:
        x, y, size = pos["qr_1"]
        x_val, y_val = validar_coordenadas(x, y, pagesize)
        pdf_canvas.drawImage(ImageReader(qr_image), x_val, y_val - size, width=size, height=size)
    
    if oficina:
        oficina_texto = oficina[:30]
        x, y_centro, font_size = pos["oficina"]
        
        pdf_canvas.saveState()
        pdf_canvas.setFont(font_name, font_size)
        pdf_canvas.setFillColorRGB(1, 1, 1)  
        
        y_centrado = calcular_y_centrado_vertical(pdf_canvas, oficina_texto, y_centro, font_name, font_size)
        
        x_val, y_val = validar_coordenadas(x, y_centrado, pagesize)
        pdf_canvas.translate(x_val, y_val)
        pdf_canvas.rotate(90)  
        pdf_canvas.drawString(0, 0, oficina_texto)
        pdf_canvas.restoreState()


def agregar_contenido_reverso(pdf_canvas: canvas.Canvas, mesa: str, paseo: str, 
                             font_normal: str, font_bold: str):
    """
    Agrega el contenido al reverso del gafete.
    Mesa y paseo en MAYÚSCULAS, NEGRITAS y color BLANCO
    """
    
    pagesize = pdf_canvas._pagesize if hasattr(pdf_canvas, '_pagesize') else (ANCHO_PUNTOS, ALTO_PUNTOS)
    pos = POS["reverso"]
    
    pdf_canvas.setFillColorRGB(1, 1, 1)  
    
    pdf_canvas.setFont(font_bold, pos["mesa"][2])  
    x_val, y_val = validar_coordenadas(pos["mesa"][0], pos["mesa"][1], pagesize)
    pdf_canvas.drawString(x_val, y_val, mesa.upper()) 
    
    pdf_canvas.setFont(font_bold, pos["paseo"][2])  
    x_val, y_val = validar_coordenadas(pos["paseo"][0], pos["paseo"][1], pagesize)
    pdf_canvas.drawString(x_val, y_val, paseo.upper())  

def generar_frente_individual(nombre: str, apellido: str, oficina: str, puesto: str,
                             qr_bytes: Optional[io.BytesIO] = None) -> bytes:
    """
    Genera la página frontal del gafete - FORMATO INDIVIDUAL
    """
    font_normal, _ = registrar_fuentes()
    
    template_path = "template_frente.pdf"
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    
    ancho_real, alto_real = obtener_dimensiones_pdf(template_path)
    
    template_reader = PdfReader(template_path)
    template_page = template_reader.pages[0]
    
    packet = io.BytesIO()
    temp_canvas = canvas.Canvas(packet, pagesize=(ancho_real, alto_real))
    
    agregar_contenido_frente(temp_canvas, nombre, apellido, oficina, puesto, qr_bytes, font_normal)
    
    temp_canvas.save()
    packet.seek(0)
    
    new_pdf = PdfReader(packet)
    new_page = new_pdf.pages[0]
    template_page.merge_page(new_page)
    
    output = PdfWriter()
    output.add_page(template_page)
    
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    return output_stream.getvalue()


def generar_reverso(mesa: str, paseo: str) -> bytes:
    """
    Genera la página reversa del gafete.
    """
    font_normal, font_bold = registrar_fuentes()
    
    template_path = "template_reverso.pdf"
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    
    ancho_real, alto_real = obtener_dimensiones_pdf(template_path)
    
    template_reader = PdfReader(template_path)
    template_page = template_reader.pages[0]
    
    packet = io.BytesIO()
    temp_canvas = canvas.Canvas(packet, pagesize=(ancho_real, alto_real))
    
    agregar_contenido_reverso(temp_canvas, mesa, paseo, font_normal, font_bold)
    
    temp_canvas.save()
    packet.seek(0)
    
    new_pdf = PdfReader(packet)
    new_page = new_pdf.pages[0]
    template_page.merge_page(new_page)
    
    output = PdfWriter()
    output.add_page(template_page)
    
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    return output_stream.getvalue()


def generate_badge(entry: Dict, qr_image: Optional[io.BytesIO], 
                  qr_conyugue: Optional[io.BytesIO] = None,
                  output_dir: str = "gafetes", debug: bool = False) -> List[str]:
    """
    Genera gafete(s) completo(s) con frente y reverso.
    Cada persona (titular y acompañante) tiene su propio gafete individual.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    nombre = entry.get("PrimerNombre", "")
    apellido = entry.get("PrimerApellido", "") 
    oficina = entry.get("Oficina", "")
    puesto = entry.get("Puesto", "")
    mesa = entry.get("Mesa", "").strip() or "Sin mesa asignada"   
    paseo = entry.get("Tour", "").strip() or "Sin tour asignado"  
    lleva_conyugue = entry.get("LLevaConyugue", False)
    
    logger.info(f"Generando gafete para {nombre} {apellido}")
    
    frente_bytes = generar_frente_individual(nombre, apellido, oficina, puesto, qr_image)
    reverso_bytes = generar_reverso(mesa, paseo)
    
    frente_reader = PdfReader(io.BytesIO(frente_bytes))
    reverso_reader = PdfReader(io.BytesIO(reverso_bytes))
    
    output = PdfWriter()
    output.add_page(frente_reader.pages[0])
    output.add_page(reverso_reader.pages[0])
    
    nombre_archivo = f"{sanitizar_nombre_archivo(apellido)}_{sanitizar_nombre_archivo(nombre)}.pdf"
    filepath = os.path.join(output_dir, nombre_archivo)
    
    with open(filepath, 'wb') as f:
        output.write(f)
    
    logger.info(f" Gafete titular guardado: {filepath}")
    generated_files.append(filepath)
    
    if lleva_conyugue and entry.get("PrimerNombreConyugue"):
        nombre_conyugue = entry.get("PrimerNombreConyugue", "")
        apellido_conyugue = entry.get("PrimerApellidoConyugue", "")
        
        logger.info(f"Generando gafete acompañante para {nombre_conyugue} {apellido_conyugue}")
        
        puesto_acompanante = "Acompañante"
        
        frente_bytes = generar_frente_individual(
            nombre_conyugue, 
            apellido_conyugue, 
            "",   
            puesto_acompanante,   
            qr_conyugue   
        )
        reverso_bytes = generar_reverso("N/A", paseo)   
        
        frente_reader = PdfReader(io.BytesIO(frente_bytes))
        reverso_reader = PdfReader(io.BytesIO(reverso_bytes))
        
        output = PdfWriter()
        output.add_page(frente_reader.pages[0])
        output.add_page(reverso_reader.pages[0])
        
        nombre_archivo = f"{sanitizar_nombre_archivo(apellido_conyugue)}_{sanitizar_nombre_archivo(nombre_conyugue)}_acompanante.pdf"
        filepath = os.path.join(output_dir, nombre_archivo)
        
        with open(filepath, 'wb') as f:
            output.write(f)
        
        logger.info(f"Gafete acompañante guardado: {filepath}")
        generated_files.append(filepath)
    
    return generated_files


def generate_debug_pdfs(output_dir: str = "gafetes"):
    """Genera PDFs de debug con posiciones marcadas."""
    
    logger.info("Generando PDFs de debug...")
    
    debug_canvas_frente = canvas.Canvas(
        os.path.join(output_dir, "debug_frente.pdf"),
        pagesize=(ANCHO_PUNTOS, ALTO_PUNTOS)
    )
    
    debug_canvas_frente.setStrokeColorRGB(0.8, 0.8, 0.8)
    debug_canvas_frente.setLineWidth(0.5)
    
    for x in range(0, int(ANCHO_PUNTOS) + 1, 100):
        debug_canvas_frente.line(x, 0, x, ALTO_PUNTOS)
    
    for y in range(0, int(ALTO_PUNTOS) + 1, 100):
        debug_canvas_frente.line(0, y, ANCHO_PUNTOS, y)
    
    debug_canvas_frente.setFillColorRGB(0, 0.5, 0)
    debug_canvas_frente.setFont('Helvetica', 10)
    for elemento, (x, y, size) in POS["frente"].items():
        debug_canvas_frente.circle(x, y, 5, fill=1)
        debug_canvas_frente.drawString(x + 10, y, f"{elemento} ({x},{y}) size={size}")
    
    debug_canvas_frente.save()
    
    debug_canvas_reverso = canvas.Canvas(
        os.path.join(output_dir, "debug_reverso.pdf"),
        pagesize=(ANCHO_PUNTOS, ALTO_PUNTOS)
    )
    
    debug_canvas_reverso.setStrokeColorRGB(0.8, 0.8, 0.8)
    debug_canvas_reverso.setLineWidth(0.5)
    
    for x in range(0, int(ANCHO_PUNTOS) + 1, 100):
        debug_canvas_reverso.line(x, 0, x, ALTO_PUNTOS)
    
    for y in range(0, int(ALTO_PUNTOS) + 1, 100):
        debug_canvas_reverso.line(0, y, ANCHO_PUNTOS, y)
    
    debug_canvas_reverso.setFillColorRGB(0.5, 0, 0.5)
    debug_canvas_reverso.setFont('Helvetica', 10)
    for elemento, (x, y, size) in POS["reverso"].items():
        debug_canvas_reverso.circle(x, y, 5, fill=1)
        debug_canvas_reverso.drawString(x + 10, y, f"{elemento} ({x},{y}) size={size}")
    
    debug_canvas_reverso.save()
    
    logger.info(" PDFs de debug generados")