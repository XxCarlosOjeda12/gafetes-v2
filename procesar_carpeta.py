#!/usr/bin/env python3
"""
Script para procesar múltiples PDFs de una carpeta y escalarlos a 9x14.5 cm
"""
import os
import sys
from pypdf import PdfReader, PdfWriter, Transformation

def cm_to_points(cm):
    """Convierte centímetros a puntos PDF (1 cm = 28.35 points)"""
    return cm * 28.35

def escalar_pagina(page, ancho_objetivo, alto_objetivo):
    """Escala una página individual a las dimensiones objetivo."""
    ancho_original = float(page.mediabox.width)
    alto_original = float(page.mediabox.height)
    
    factor_ancho = ancho_objetivo / ancho_original
    factor_alto = alto_objetivo / alto_original
    factor_escala = min(factor_ancho, factor_alto)
    
    nuevo_ancho = ancho_original * factor_escala
    nuevo_alto = alto_original * factor_escala
    
    offset_x = (ancho_objetivo - nuevo_ancho) / 2
    offset_y = (alto_objetivo - nuevo_alto) / 2
    
    op = Transformation().scale(sx=factor_escala, sy=factor_escala)
    page.add_transformation(op)
    
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (ancho_objetivo, alto_objetivo)
    
    if offset_x > 0 or offset_y > 0:
        op_centro = Transformation().translate(tx=offset_x, ty=offset_y)
        page.add_transformation(op_centro)
    
    return page, factor_escala

def procesar_pdf(archivo_entrada, carpeta_salida, ancho_cm=9, alto_cm=14.5):
    """
    Procesa un PDF individual, escalándolo y dividiéndolo en frente/reverso.
    
    Args:
        archivo_entrada: Path del PDF original
        carpeta_salida: Carpeta donde guardar los resultados
        ancho_cm: Ancho objetivo en centímetros
        alto_cm: Alto objetivo en centímetros
    
    Returns:
        tuple: (archivo_frente, archivo_reverso) o None si hay error
    """
    try:
        ancho_objetivo = cm_to_points(ancho_cm)
        alto_objetivo = cm_to_points(alto_cm)
        
        reader = PdfReader(archivo_entrada)
        num_paginas = len(reader.pages)
        
        if num_paginas < 2:
            print(f"  ⚠️  Omitiendo {os.path.basename(archivo_entrada)} - Solo tiene {num_paginas} página(s)")
            return None
        
        # Generar nombres de archivo de salida
        nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
        archivo_frente = os.path.join(carpeta_salida, f"{nombre_base}_frente.pdf")
        archivo_reverso = os.path.join(carpeta_salida, f"{nombre_base}_reverso.pdf")
        
        # Procesar página 1 (frente)
        page_frente, _ = escalar_pagina(reader.pages[0], ancho_objetivo, alto_objetivo)
        writer_frente = PdfWriter()
        writer_frente.add_page(page_frente)
        with open(archivo_frente, "wb") as f:
            writer_frente.write(f)
        
        # Procesar página 2 (reverso)
        page_reverso, _ = escalar_pagina(reader.pages[1], ancho_objetivo, alto_objetivo)
        writer_reverso = PdfWriter()
        writer_reverso.add_page(page_reverso)
        with open(archivo_reverso, "wb") as f:
            writer_reverso.write(f)
        
        return (archivo_frente, archivo_reverso)
        
    except Exception as e:
        print(f"  ✗ Error procesando {os.path.basename(archivo_entrada)}: {e}")
        return None

def procesar_carpeta(carpeta_entrada, carpeta_salida):
    """
    Procesa todos los PDFs de una carpeta.
    
    Args:
        carpeta_entrada: Carpeta con los PDFs originales
        carpeta_salida: Carpeta donde guardar los resultados
    """
    print(f"=== PROCESAMIENTO MASIVO DE GAFETES ===")
    print(f"Carpeta de entrada: {carpeta_entrada}")
    print(f"Carpeta de salida: {carpeta_salida}")
    print()
    
    # Crear carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"✓ Carpeta de salida creada\n")
    
    # Buscar todos los PDFs en la carpeta de entrada
    archivos_pdf = [
        f for f in os.listdir(carpeta_entrada) 
        if f.endswith('.pdf') and os.path.isfile(os.path.join(carpeta_entrada, f))
    ]
    
    if not archivos_pdf:
        print(f"✗ No se encontraron archivos PDF en {carpeta_entrada}")
        return
    
    print(f"Archivos PDF encontrados: {len(archivos_pdf)}")
    print("=" * 60)
    
    exitosos = 0
    errores = 0
    omitidos = 0
    
    for i, nombre_archivo in enumerate(archivos_pdf, 1):
        archivo_completo = os.path.join(carpeta_entrada, nombre_archivo)
        print(f"\n[{i}/{len(archivos_pdf)}] Procesando: {nombre_archivo}")
        
        resultado = procesar_pdf(archivo_completo, carpeta_salida)
        
        if resultado:
            frente, reverso = resultado
            print(f"  ✓ Generado: {os.path.basename(frente)}")
            print(f"  ✓ Generado: {os.path.basename(reverso)}")
            exitosos += 1
        elif resultado is None:
            omitidos += 1
        else:
            errores += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 60)
    print(f"Total de archivos procesados: {len(archivos_pdf)}")
    print(f"  ✓ Exitosos: {exitosos}")
    if omitidos > 0:
        print(f"  ⚠️  Omitidos: {omitidos}")
    if errores > 0:
        print(f"  ✗ Con errores: {errores}")
    
    print(f"\nArchivos generados en: {carpeta_salida}")
    print(f"Total de archivos creados: {exitosos * 2} ({exitosos} pares)")

def main():
    if len(sys.argv) < 3:
        print("Uso: python procesar_carpeta.py <carpeta_entrada> <carpeta_salida>")
        print("\nEjemplo:")
        print("  python procesar_carpeta.py ./gafetes_originales ./gafetes_escalados")
        print("\nProcesa todos los PDFs de la carpeta de entrada, los escala a 9x14.5 cm")
        print("y guarda los archivos _frente.pdf y _reverso.pdf en la carpeta de salida.")
        sys.exit(1)
    
    carpeta_entrada = sys.argv[1]
    carpeta_salida = sys.argv[2]
    
    if not os.path.isdir(carpeta_entrada):
        print(f"Error: '{carpeta_entrada}' no es un directorio válido")
        sys.exit(1)
    
    try:
        procesar_carpeta(carpeta_entrada, carpeta_salida)
        print("\n✓ Procesamiento completado exitosamente")
    except Exception as e:
        print(f"\n✗ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()