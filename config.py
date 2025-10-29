#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de configuración central para el generador de gafetes.
Centraliza todas las constantes y configuraciones del sistema.
"""

import os
from typing import Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = BASE_DIR
TEMPLATE_FRENTE = os.path.join(TEMPLATE_DIR, "template_frente.pdf")
TEMPLATE_REVERSO = os.path.join(TEMPLATE_DIR, "template_reverso.pdf")

DEFAULT_OUTPUT_DIR = "gafetes"
DEFAULT_QRS_DIR = "qrs"
DEFAULT_LOG_DIR = "logs"

PAGE_WIDTH_MM = 281
PAGE_HEIGHT_MM = 453

MM_TO_POINTS = 2.834645669

PAGE_WIDTH_POINTS = PAGE_WIDTH_MM * MM_TO_POINTS
PAGE_HEIGHT_POINTS = PAGE_HEIGHT_MM * MM_TO_POINTS

POSITIONS: Dict[str, Dict[str, Tuple[float, float, float]]] = {
    "frente": {
        "nombre": (320, 880, 65),
        "apellido": (320, 800, 65),
        "puesto": (480, 630, 32),
        "oficina": (100, 800, 70),
        "qr_1": (660, 860, 150),
    },
    "reverso": {
        "mesa": (315, 1121, 22),
        "paseo": (150, 1055, 22),
    },
    "frente_acompanante": {
        "nombre_titular": (320, 950, 40),
        "apellido_titular": (320, 900, 40),
        "nombre_acompanante": (320, 750, 40),
        "apellido_acompanante": (320, 700, 40),
        "puesto": (480, 630, 32),
        "oficina": (100, 800, 70),
        "qr_titular": (620, 950, 120),
        "qr_acompanante": (620, 750, 120),
    }
}

FONT_PATHS = {
    "windows": "C:/Windows/Fonts/arial.ttf",
    "linux": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "mac": "/Library/Fonts/Arial.ttf",
    "fallback": "Helvetica-Bold"
}

MESAS_VALIDAS: List[str] = [
    "Valuación",
    "Grúas",
    "Q Salud",
    "Proyectos estratégicos",
    "Productos y Tarifas",
    "Verificaciones"
]

PASEOS_VALIDOS: List[str] = [
    "Por el Centro Histórico",
    "Museando Ando",
    "Vamos Pa'l Mercado",
    "Colores de México"
]

EXCEL_REQUIRED_COLUMNS: List[str] = [
    "Puesto",
    "PrimerNombre", 
    "PrimerApellido",
    "Oficina",
    "Tour",
    "Mesa",
    "LLevaConyugue",
    "PrimerNombreConyugue",
    "PrimerApellidoConyugue", 
    "QR",
    "QR_Conyugue"
]

TRUE_VALUES = {"SI", "SÍ", "S", "YES", "Y", "1", "TRUE", "VERDADERO"}

QR_BASE_URL = "https://evento-directores.qualitaseventos.mx/downloadQr/{codigo}/"

QR_DOWNLOAD_TIMEOUT = 10
QR_MAX_RETRIES = 2
QR_RETRY_DELAY = 1

QR_BOX_SIZE = 10
QR_BORDER = 4
QR_DEFAULT_SIZE = (200, 200)

DEFAULT_WORKERS = 8

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

DEFAULT_LOG_LEVEL = "INFO"

CACHE_MAX_AGE_DAYS = 30

MAX_ATTENDEES = 10000

MAX_EXCEL_SIZE_MB = 50

MAX_ERRORS_BEFORE_ABORT = 100

MESSAGES = {
    "welcome": "GENERADOR DE GAFETES - REUNIÓN ANUAL DE DIRECTORES 2025",
    "validation_start": "Validando entorno y configuración...",
    "reading_excel": "Leyendo archivo Excel: {file}",
    "processing_attendee": "[{current}/{total}] Procesando: {name} {surname}",
    "badge_generated": "Gafete generado: {file}",
    "process_complete": "Proceso completado exitosamente",
    "process_failed": "Proceso falló con {errors} errores",
    "dry_run_mode": "MODO DRY-RUN: Solo validación, no se generarán archivos"
}

DEBUG_ENABLED = False

DEBUG_GENERATE_PDFS = True

DEBUG_COLORS = {
    "grid": (0.8, 0.8, 0.8),
    "border": (1, 0, 0),
    "center": (0, 0, 1),
    "positions_front": (0, 0.5, 0),
    "positions_back": (0.5, 0, 0.5)
}

def get_font_path() -> str:
    """
    Obtiene la ruta de la fuente según el sistema operativo.
    
    Returns:
        Ruta de la fuente o nombre de fuente fallback
    """
    import platform
    
    system = platform.system().lower()
    
    if 'windows' in system:
        font = FONT_PATHS.get('windows')
    elif 'darwin' in system or 'mac' in system:
        font = FONT_PATHS.get('mac')
    elif 'linux' in system:
        font = FONT_PATHS.get('linux')
    else:
        font = FONT_PATHS.get('fallback')
    
    if font and font != FONT_PATHS['fallback']:
        if os.path.exists(font):
            return font
    
    return FONT_PATHS['fallback']


def validate_config() -> List[str]:
    """
    Valida la configuración del sistema.
    
    Returns:
        Lista de advertencias (vacía si todo está bien)
    """
    warnings = []
    
    if not os.path.exists(TEMPLATE_FRENTE):
        warnings.append(f"Template frente no encontrado: {TEMPLATE_FRENTE}")
    
    if not os.path.exists(TEMPLATE_REVERSO):
        warnings.append(f"Template reverso no encontrado: {TEMPLATE_REVERSO}")
    
    if PAGE_WIDTH_POINTS <= 0 or PAGE_HEIGHT_POINTS <= 0:
        warnings.append(f"Tamaño de página inválido: {PAGE_WIDTH_POINTS}x{PAGE_HEIGHT_POINTS}")
    
    if MAX_ATTENDEES <= 0:
        warnings.append(f"Límite de asistentes inválido: {MAX_ATTENDEES}")
    
    return warnings


def get_config_summary() -> str:
    """
    Genera un resumen de la configuración actual.
    
    Returns:
        String con el resumen de configuración
    """
    lines = [
        "=" * 60,
        "CONFIGURACIÓN DEL SISTEMA",
        "=" * 60,
        f"Templates:",
        f"   Frente: {os.path.basename(TEMPLATE_FRENTE)}",
        f"   Reverso: {os.path.basename(TEMPLATE_REVERSO)}",
        f"Página:",
        f"   Tamaño: {PAGE_WIDTH_MM}×{PAGE_HEIGHT_MM} mm",
        f"   En puntos: {PAGE_WIDTH_POINTS:.1f}×{PAGE_HEIGHT_POINTS:.1f}",
        f"QRs:",
        f"   URL base: {QR_BASE_URL[:50]}...",
        f"   Timeout: {QR_DOWNLOAD_TIMEOUT}s",
        f"   Reintentos: {QR_MAX_RETRIES}",
        f"Sistema:",
        f"   Max asistentes: {MAX_ATTENDEES}",
        f"   Max errores: {MAX_ERRORS_BEFORE_ABORT}",
        f"   Workers: {DEFAULT_WORKERS}",
        "=" * 60
    ]
    
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_config_summary())
    
    warnings = validate_config()
    if warnings:
        print("\nADVERTENCIAS:")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print("\nConfiguración válida")
    
    font = get_font_path()
    print(f"\nFuente detectada: {font}")
