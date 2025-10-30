#!/usr/bin/env python3
"""
Script para generar automáticamente el archivo JSON de lista de gafetes
a partir de archivos *_frente.pdf y *_reverso.pdf en una carpeta.
"""
import os
import sys
import json
import re
from pathlib import Path

def extraer_numero(nombre_archivo):
    """
    Extrae el número del archivo para ordenamiento numérico.
    
    Args:
        nombre_archivo: Nombre del archivo (sin extensión)
        
    Returns:
        Tupla numérica para ordenamiento
    """
    # Buscar patrones como "1.", "10.1", "104.1", etc.
    patron = r'^(\d+(?:\.\d+)?)'
    coincidencia = re.match(patron, nombre_archivo)
    
    if coincidencia:
        numero_str = coincidencia.group(1)
        # Convertir a tupla de números para ordenamiento correcto
        partes = numero_str.split('.')
        return tuple(int(part) for part in partes)
    else:
        # Si no tiene número, usar 0 para que aparezca primero
        return (0,)

def buscar_pares_gafetes(directorio):
    """
    Busca pares de archivos frente-reverso en un directorio.
    
    Args:
        directorio: Path del directorio donde buscar
        
    Returns:
        Lista de diccionarios con pares frente-reverso, ordenados numéricamente
    """
    frentes = {}
    reversos = {}
    
    # Buscar todos los archivos PDF
    for archivo in os.listdir(directorio):
        if not archivo.endswith('.pdf'):
            continue
        
        ruta_completa = os.path.join(directorio, archivo)
        
        # Identificar frentes
        if '_frente.pdf' in archivo:
            base_name = archivo.replace('_frente.pdf', '')
            frentes[base_name] = ruta_completa
            
        # Identificar reversos
        elif '_reverso.pdf' in archivo:
            base_name = archivo.replace('_reverso.pdf', '')
            reversos[base_name] = ruta_completa
    
    # Emparejar frentes con reversos
    pares = []
    nombres_base = set(frentes.keys()) | set(reversos.keys())
    
    # Ordenar nombres base numéricamente
    nombres_base_ordenados = sorted(nombres_base, key=extraer_numero)
    
    for nombre in nombres_base_ordenados:
        if nombre in frentes and nombre in reversos:
            pares.append({
                'frente': frentes[nombre],
                'reverso': reversos[nombre]
            })
            print(f"✓ Par encontrado: {nombre}")
        elif nombre in frentes:
            print(f"⚠️  Advertencia: Falta reverso para {nombre}")
        elif nombre in reversos:
            print(f"⚠️  Advertencia: Falta frente para {nombre}")
    
    return pares

def generar_lista_json(directorio, archivo_salida='lista_gafetes.json'):
    """
    Genera el archivo JSON con la lista de gafetes.
    
    Args:
        directorio: Directorio donde buscar los PDFs
        archivo_salida: Nombre del archivo JSON de salida
    """
    print(f"Buscando archivos en: {directorio}")
    print("=" * 60)
    
    pares = buscar_pares_gafetes(directorio)
    
    if not pares:
        print("\n✗ No se encontraron pares de gafetes")
        print("\nAsegúrate de que tus archivos tengan el formato:")
        print("  - nombre_frente.pdf")
        print("  - nombre_reverso.pdf")
        return False
    
    print(f"\n{'=' * 60}")
    print(f"Total de pares encontrados: {len(pares)}")
    
    # Crear estructura JSON
    data = {
        'gafetes': pares
    }
    
    # Guardar archivo
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Archivo generado exitosamente: {archivo_salida}")
    print(f"\nAhora puedes ejecutar:")
    print(f"  python distribuir_gafetes.py {archivo_salida} gafetes_imprimir.pdf")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python generar_lista.py <directorio> [archivo_salida.json]")
        print("\nEjemplo:")
        print("  python generar_lista.py ./gafetes")
        print("  python generar_lista.py ./gafetes mi_lista.json")
        print("\nBusca todos los archivos *_frente.pdf y *_reverso.pdf")
        print("en el directorio y genera el JSON automáticamente.")
        sys.exit(1)
    
    directorio = sys.argv[1]
    
    if not os.path.isdir(directorio):
        print(f"Error: '{directorio}' no es un directorio válido")
        sys.exit(1)
    
    # Determinar nombre de archivo de salida
    if len(sys.argv) >= 3:
        archivo_salida = sys.argv[2]
    else:
        archivo_salida = 'lista_gafetes.json'
    
    try:
        success = generar_lista_json(directorio, archivo_salida)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()