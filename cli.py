#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo CLI para el generador de gafetes.
Maneja argumentos de línea de comandos y orquesta el proceso completo.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Optional
from datetime import datetime

import excel
import qrs
import generator
import utils

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        Namespace con los argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Generador Automático de Gafetes para Reunión Anual de Directores 2025",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Procesar Excel con descarga de QRs
  python gafetes_generator.py --excel asistentes.xlsx

  # Usar caché para QRs y hoja específica
  python gafetes_generator.py --excel asistentes.xlsx --sheet "Hoja1" --qr-strategy cache

  # Modo dry-run (solo validación)
  python gafetes_generator.py --excel asistentes.xlsx --dry-run

  # Descarga paralela con 10 workers
  python gafetes_generator.py --excel asistentes.xlsx --qr-strategy cache --workers 10

  # Modo debug con logs detallados
  python gafetes_generator.py --excel asistentes.xlsx --debug --log-level DEBUG
"""
    )
    
    parser.add_argument(
        "--excel",
        type=str,
        required=True,
        help="Ruta al archivo Excel con los datos de asistentes"
    )
    
    parser.add_argument(
        "--sheet",
        type=str,
        default=None,
        help="Nombre de la hoja del Excel a procesar (por defecto la primera)"
    )
    
    parser.add_argument(
        "--qr-strategy",
        choices=["download", "cache"],
        default="download",
        help="Estrategia para QRs: 'download' no guarda, 'cache' guarda localmente (default: download)"
    )
    
    parser.add_argument(
        "--qrs-dir",
        type=str,
        default="qrs",
        help="Directorio para caché de QRs (default: qrs/)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="gafetes",
        help="Directorio de salida para PDFs (default: gafetes/)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Generar PDFs de debug con posiciones"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo validar sin generar archivos"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Número de workers para descarga paralela (default: 8)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Nivel de logging (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Archivo para guardar logs (opcional)"
    )
    
    parser.add_argument(
        "--clean-cache",
        action="store_true",
        help="Limpiar caché de QRs antiguos antes de empezar"
    )
    
    parser.add_argument(
        "--prefetch",
        action="store_true",
        help="Pre-descargar todos los QRs antes de generar gafetes"
    )
    
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="Permitir generación local de QR si falla descarga (NO válido para escaneo)"
    )
    
    return parser.parse_args()


def validate_environment() -> List[str]:
    """
    Valida el entorno antes de ejecutar.
    
    Returns:
        Lista de advertencias (vacía si todo está bien)
    """
    warnings = []
    
    templates_requeridos = ["template_frente.pdf", "template_reverso.pdf"]
    templates_faltantes = utils.validar_templates(templates_requeridos)
    
    if templates_faltantes:
        for template in templates_faltantes:
            warnings.append(f"Template faltante: {template}")
    
    test_dirs = [".", "gafetes", "qrs"]
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            test_file = os.path.join(dir_path, ".test_write")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                warnings.append(f"Sin permisos de escritura en {dir_path}: {e}")
    
    return warnings


def process_attendees(
    attendees: List[Dict],
    args: argparse.Namespace,
    stats: utils.GeneratorStats
) -> int:
    """
    Procesa la lista de asistentes y genera los gafetes.
    
    Args:
        attendees: Lista de diccionarios con datos de asistentes
        args: Argumentos de línea de comandos
        stats: Objeto de estadísticas
        
    Returns:
        Número de errores encontrados
    """
    errors = 0
    
    if args.prefetch and not args.dry_run:
        logger.info("Pre-descargando códigos QR...")
        
        all_codes = []
        for entry in attendees:
            if entry.get("QR"):
                all_codes.append(entry["QR"])
            if entry.get("LLevaConyugue") and entry.get("QR_Conyugue"):
                all_codes.append(entry["QR_Conyugue"])
        
        if all_codes:
            qr_results = qrs.prefetch_qrs(
                all_codes,
                strategy=args.qr_strategy,
                qrs_dir=args.qrs_dir,
                workers=args.workers,
                allow_fallback=args.allow_fallback
            )
            logger.info(f"Pre-descarga completada: {len(qr_results)} QRs procesados")
    
    for idx, entry in enumerate(attendees, 1):
        nombre = entry.get("PrimerNombre", "")
        apellido = entry.get("PrimerApellido", "")
        lleva_conyugue = entry.get("LLevaConyugue", False)
        
        logger.info(f"[{idx}/{len(attendees)}] Procesando: {nombre} {apellido}")
        stats.filas_procesadas += 1
        
        if args.dry_run:
            logger.info(f"  [DRY-RUN] Validado: {nombre} {apellido}")
            if lleva_conyugue:
                logger.info(f"  [DRY-RUN] Con acompañante: {entry.get('PrimerNombreConyugue')} {entry.get('PrimerApellidoConyugue')}")
            continue
        
        try:
            qr_titular = None
            if entry.get("QR"):
                logger.debug(f"  Obteniendo QR titular: {entry['QR']}")
                try:
                    qr_titular = qrs.get_qr_image(
                        entry["QR"],
                        strategy=args.qr_strategy,
                        qrs_dir=args.qrs_dir,
                        allow_fallback=args.allow_fallback
                    )
                    
                    if "downloadQr" in entry["QR"] or entry["QR"].startswith("http"):
                        stats.qrs_descargados += 1
                    elif os.path.exists(os.path.join(args.qrs_dir, f"{entry['QR']}.png")):
                        stats.qrs_cache += 1
                    else:
                        stats.qrs_generados_local += 1
                        
                except Exception as e:
                    if not args.allow_fallback:
                        raise
                    else:
                        logger.warning(f"  No se pudo obtener QR titular: {e}")
            
            qr_conyugue = None
            if lleva_conyugue and entry.get("QR_Conyugue"):
                logger.debug(f"  Obteniendo QR acompañante: {entry['QR_Conyugue']}")
                try:
                    qr_conyugue = qrs.get_qr_image(
                        entry["QR_Conyugue"],
                        strategy=args.qr_strategy,
                        qrs_dir=args.qrs_dir,
                        allow_fallback=args.allow_fallback
                    )
                    
                    if "downloadQr" in entry["QR_Conyugue"] or entry["QR_Conyugue"].startswith("http"):
                        stats.qrs_descargados += 1
                    elif os.path.exists(os.path.join(args.qrs_dir, f"{entry['QR_Conyugue']}.png")):
                        stats.qrs_cache += 1
                    else:
                        stats.qrs_generados_local += 1
                        
                except Exception as e:
                    if not args.allow_fallback:
                        raise
                    else:
                        logger.warning(f"  No se pudo obtener QR acompañante: {e}")
            
            generated_files = generator.generate_badge(
                entry,
                qr_titular,
                qr_conyugue,
                output_dir=args.output_dir,
                debug=args.debug
            )
            
            for filepath in generated_files:
                if "_acompanante.pdf" in filepath:
                    stats.gafetes_acompanantes += 1
                    logger.info(f"  ✓ Gafete acompañante generado: {os.path.basename(filepath)}")
                else:
                    stats.gafetes_titulares += 1
                    logger.info(f"  ✓ Gafete titular generado: {os.path.basename(filepath)}")
            
        except Exception as e:
            errors += 1
            stats.filas_omitidas += 1
            error_msg = f"Error procesando {nombre} {apellido}: {str(e)}"
            stats.agregar_error(error_msg)
            logger.error(f"  ✗ {error_msg}")
    
    return errors


def main():
    """Función principal del CLI."""
    args = parse_arguments()
    
    utils.setup_logging(level=args.log_level, log_file=args.log_file)
    
    print("=" * 80)
    print("GENERADOR DE GAFETES - REUNIÓN ANUAL DE DIRECTORES 2025")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Excel: {args.excel}")
    print(f"Estrategia QR: {args.qr_strategy}")
    print(f"Directorio salida: {args.output_dir}")
    
    if args.dry_run:
        print("\n🔍 MODO DRY-RUN: Solo validación, no se generarán archivos")
    
    if args.allow_fallback:
        print("\n ATENCIÓN: Modo fallback habilitado")
        print("   Los QRs generados localmente NO funcionarán para el escaneo en el evento")
    
    print("=" * 80)
    
    logger.info("Validando entorno...")
    warnings = validate_environment()
    
    if warnings:
        print("\n ADVERTENCIAS:")
        for warning in warnings:
            print(f"  • {warning}")
        
        if any("Template faltante" in w for w in warnings) and not args.dry_run:
            print("\n No se puede continuar sin los templates. Abortando.")
            sys.exit(1)
    
    if not args.dry_run:
        utils.crear_directorios([args.output_dir, args.qrs_dir])
    
    if args.clean_cache and os.path.exists(args.qrs_dir):
        logger.info("Limpiando caché de QRs...")
        deleted = qrs.clean_cache(args.qrs_dir)
        print(f" Caché limpiado: {deleted} archivos eliminados")
    
    stats = utils.GeneratorStats()
    
    try:
        print(f"\n Leyendo archivo Excel: {args.excel}")
        attendees = excel.read_attendees(args.excel, args.sheet)
        
        if not attendees:
            print(" No se encontraron asistentes válidos en el archivo.")
            sys.exit(0)
        
        print(f" {len(attendees)} asistentes encontrados")
        
        con_acompanante = sum(1 for a in attendees if a.get("LLevaConyugue"))
        if con_acompanante:
            print(f"  • {con_acompanante} con acompañante")
            print(f"  • {len(attendees) - con_acompanante} sin acompañante")
        
        print(f"\n{' ' if args.dry_run else '🚀'} Procesando asistentes...")
        errors = process_attendees(attendees, args, stats)
        
        print(stats.generar_resumen())
        
        if not args.dry_run and stats.filas_procesadas > 0:
            resumen_file = stats.guardar_resumen(
                os.path.join(args.output_dir, "resumen_generacion.txt")
            )
            print(f"\n Resumen guardado en: {resumen_file}")
        
        if args.debug and not args.dry_run:
            generator.generate_debug_pdfs(args.output_dir)
            print(f"\n PDFs de debug generados en {args.output_dir}/")
        
        if errors > 0:
            print(f"\n Proceso completado con {errors} errores")
            sys.exit(1)
        else:
            print("\n Proceso completado exitosamente")
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n Error de validación: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n Proceso interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        logger.exception("Error inesperado")
        print(f"\n Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
