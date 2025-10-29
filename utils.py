#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de utilidades compartidas para el generador de gafetes.
"""

import os
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configura el sistema de logging para toda la aplicación.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo opcional para guardar logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=handlers
    )


def sanitizar_nombre_archivo(texto: str) -> str:
    """
    Elimina caracteres no válidos para nombres de archivo.
    
    Args:
        texto: Texto a sanitizar
        
    Returns:
        Texto sanitizado
    """
    texto = re.sub(r'[^\w\s-]', '', texto.strip())
    texto = re.sub(r'[-\s]+', '_', texto)
    texto = texto.strip('_')
    
    return texto or "sin_nombre"


def normalizar_string(texto: str) -> str:
    """
    Normaliza un string removiendo espacios extras y caracteres especiales.
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not texto:
        return ""
    
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    texto = ''.join(char for char in texto if ord(char) >= 32)
    
    return texto


def crear_directorios(directorios: List[str]) -> None:
    """
    Crea los directorios necesarios si no existen.
    
    Args:
        directorios: Lista de rutas de directorios a crear
    """
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
        logging.debug(f"Directorio asegurado: {directorio}")


def validar_templates(templates_requeridos: List[str]) -> List[str]:
    """
    Valida que existan los archivos de plantilla necesarios.
    
    Args:
        templates_requeridos: Lista de archivos de plantilla requeridos
        
    Returns:
        Lista de plantillas faltantes
    """
    faltantes = []
    for template in templates_requeridos:
        if not os.path.exists(template):
            faltantes.append(template)
            logging.warning(f"Plantilla faltante: {template}")
        else:
            logging.debug(f"Plantilla encontrada: {template}")
    
    return faltantes


class GeneratorStats:
    """Clase para llevar estadísticas del proceso de generación."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reinicia todas las estadísticas."""
        self.filas_procesadas = 0
        self.gafetes_titulares = 0
        self.gafetes_acompanantes = 0
        self.filas_omitidas = 0
        self.qrs_descargados = 0
        self.qrs_cache = 0
        self.qrs_generados_local = 0
        self.errores = []
        self.tiempo_inicio = datetime.now()
        
    def agregar_error(self, mensaje: str):
        """Agrega un mensaje de error a la lista."""
        self.errores.append({
            'timestamp': datetime.now(),
            'mensaje': mensaje
        })
        logging.error(mensaje)
    
    def generar_resumen(self) -> str:
        """
        Genera un resumen legible del proceso.
        
        Returns:
            String con el resumen formateado
        """
        tiempo_total = (datetime.now() - self.tiempo_inicio).total_seconds()
        
        resumen = []
        resumen.append("\n" + "=" * 80)
        resumen.append("RESUMEN DE GENERACIÓN DE GAFETES")
        resumen.append("=" * 80)
        resumen.append(f"\n ESTADÍSTICAS GENERALES:")
        resumen.append(f"   • Tiempo total: {tiempo_total:.2f} segundos")
        resumen.append(f"   • Filas procesadas: {self.filas_procesadas}")
        resumen.append(f"   • Filas omitidas: {self.filas_omitidas}")
        
        resumen.append(f"\n GAFETES GENERADOS:")
        resumen.append(f"   • Titulares: {self.gafetes_titulares}")
        resumen.append(f"   • Acompañantes: {self.gafetes_acompanantes}")
        resumen.append(f"   • TOTAL: {self.gafetes_titulares + self.gafetes_acompanantes}")
        
        resumen.append(f"\n CÓDIGOS QR:")
        resumen.append(f"   • Descargados: {self.qrs_descargados}")
        resumen.append(f"   • Desde caché: {self.qrs_cache}")
        resumen.append(f"   • Generados localmente: {self.qrs_generados_local}")
        
        if self.errores:
            resumen.append(f"\n ERRORES ENCONTRADOS: {len(self.errores)}")
            for error in self.errores[:5]:
                resumen.append(f"   • {error['mensaje'][:100]}")
            if len(self.errores) > 5:
                resumen.append(f"   ... y {len(self.errores) - 5} errores más")
        
        total_esperado = self.filas_procesadas
        total_generado = self.gafetes_titulares + self.gafetes_acompanantes
        
        if total_esperado > 0:
            tasa_exito = (self.filas_procesadas - self.filas_omitidas) / self.filas_procesadas * 100
            resumen.append(f"\n TASA DE ÉXITO: {tasa_exito:.1f}%")
        
        resumen.append("\n" + "=" * 80)
        
        return "\n".join(resumen)
    
    def guardar_resumen(self, archivo: str = "resumen_generacion.txt"):
        """
        Guarda el resumen en un archivo.
        
        Args:
            archivo: Ruta del archivo donde guardar el resumen
        """
        resumen = self.generar_resumen()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(archivo)
        archivo_final = f"{base}_{timestamp}{ext}"
        
        with open(archivo_final, 'w', encoding='utf-8') as f:
            f.write(resumen)
        
        logging.info(f"Resumen guardado en: {archivo_final}")
        return archivo_final


def formato_tabla(headers: List[str], rows: List[List[str]], max_width: int = 120) -> str:
    """
    Formatea datos como tabla ASCII para mostrar en consola.
    
    Args:
        headers: Lista de encabezados
        rows: Lista de filas (cada fila es una lista de valores)
        max_width: Ancho máximo de la tabla
        
    Returns:
        String con la tabla formateada
    """
    col_widths = []
    for i, header in enumerate(headers):
        max_len = len(header)
        for row in rows:
            if i < len(row):
                max_len = max(max_len, len(str(row[i])))
        col_widths.append(min(max_len, max_width // len(headers)))
    
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    table = [separator]
    
    header_row = "|"
    for header, width in zip(headers, col_widths):
        header_row += f" {header[:width]:^{width}} |"
    table.append(header_row)
    table.append(separator)
    
    for row in rows:
        row_str = "|"
        for value, width in zip(row, col_widths):
            value_str = str(value)[:width]
            row_str += f" {value_str:<{width}} |"
        table.append(row_str)
    
    table.append(separator)
    
    return "\n".join(table)


def limpiar_archivos_temporales(patron: str = "debug_*.pdf") -> int:
    """
    Elimina archivos temporales que coincidan con el patrón.
    
    Args:
        patron: Patrón de archivos a eliminar (glob pattern)
        
    Returns:
        Número de archivos eliminados
    """
    eliminados = 0
    
    for archivo in Path(".").glob(patron):
        try:
            archivo.unlink()
            eliminados += 1
            logging.debug(f"Eliminado archivo temporal: {archivo}")
        except Exception as e:
            logging.warning(f"No se pudo eliminar {archivo}: {e}")
    
    if eliminados > 0:
        logging.info(f"Archivos temporales eliminados: {eliminados}")
    
    return eliminados


def validar_configuracion(config: Dict) -> List[str]:
    """
    Valida la configuración de la aplicación.
    
    Args:
        config: Diccionario de configuración
        
    Returns:
        Lista de mensajes de advertencia
    """
    advertencias = []
    
    dirs_requeridos = config.get('directorios', [])
    for dir_path in dirs_requeridos:
        if not os.path.exists(dir_path):
            advertencias.append(f"Directorio no existe (se creará): {dir_path}")
    
    templates = config.get('templates', [])
    for template in templates:
        if not os.path.exists(template):
            advertencias.append(f"Template no encontrado: {template}")
    
    return advertencias


if __name__ == "__main__":
    print("=== Pruebas del módulo utils ===\n")
    
    print("1. Sanitización de nombres:")
    nombres_prueba = [
        "Juan García",
        "María José/López",
        "Pedro@#$%123",
        "   espacios   múltiples   ",
        ""
    ]
    
    for nombre in nombres_prueba:
        sanitizado = sanitizar_nombre_archivo(nombre)
        print(f"   '{nombre}' → '{sanitizado}'")
    
    print("\n2. Sistema de estadísticas:")
    stats = GeneratorStats()
    stats.filas_procesadas = 100
    stats.gafetes_titulares = 95
    stats.gafetes_acompanantes = 30
    stats.filas_omitidas = 5
    stats.qrs_descargados = 80
    stats.qrs_cache = 20
    stats.qrs_generados_local = 25
    stats.agregar_error("Error de prueba 1")
    stats.agregar_error("Error de prueba 2")
    
    print(stats.generar_resumen())
    
    print("\n3. Formato de tabla:")
    headers = ["Nombre", "Apellido", "Oficina", "Mesa"]
    rows = [
        ["Juan", "García", "CDMX", "Valuación"],
        ["María", "López", "Guadalajara", "Grúas"],
        ["Pedro", "Martínez", "Monterrey", "Q Salud"]
    ]
    
    print(formato_tabla(headers, rows))
    
    print("\n=== Pruebas completadas ===")
