#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de pruebas rápidas para el generador de gafetes.
Ejecuta diferentes escenarios de prueba.
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado."""
    print("\n" + "=" * 70)
    print(f" {description}")
    print("=" * 70)
    print(f"Comando: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(" Éxito")
    else:
        print(f" Error (código: {result.returncode})")
    
    return result.returncode


def main():
    """Ejecuta una serie de pruebas."""
    
    print("=" * 70)
    print("SUITE DE PRUEBAS - GENERADOR DE GAFETES")
    print("=" * 70)
    
    if not os.path.exists("ejemplos/ejemplo_asistentes.xlsx"):
        print("\n Primero genera el archivo de ejemplo:")
        print("   python create_sample_excel.py")
        return
    
    tests = [
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --dry-run",
            "Test 1: Validación sin generar archivos (dry-run)"
        ),
        
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --output-dir test_output/basico",
            "Test 2: Generación básica de gafetes"
        ),
        
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --qr-strategy cache --qrs-dir test_qrs --output-dir test_output/cache",
            "Test 3: Generación con caché de QRs"
        ),
        
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --debug --output-dir test_output/debug",
            "Test 4: Generación con PDFs de debug"
        ),
        
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --qr-strategy cache --prefetch --workers 4 --output-dir test_output/prefetch",
            "Test 5: Generación con prefetch paralelo"
        ),
        
        (
            "python gafetes_generator.py --excel ejemplos/ejemplo_invalido.xlsx --dry-run",
            "Test 6: Validación de archivo inválido (debe fallar)"
        ),
    ]
    
    results = []
    
    for cmd, description in tests:
        start_time = time.time()
        returncode = run_command(cmd, description)
        elapsed_time = time.time() - start_time
        
        results.append({
            'test': description,
            'success': returncode == 0 if "debe fallar" not in description else returncode != 0,
            'time': elapsed_time
        })
        
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        status = " PASÓ" if result['success'] else " FALLÓ"
        print(f"{i}. {result['test'][:50]:<50} {status} ({result['time']:.2f}s)")
    
    total_passed = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print("\n" + "-" * 70)
    print(f"Total: {total_passed}/{total_tests} pruebas pasadas")
    
    if total_passed == total_tests:
        print(" ¡Todas las pruebas pasaron!")
    
    if os.path.exists("test_output"):
        print("\n" + "=" * 70)
        print("ARCHIVOS GENERADOS")
        print("=" * 70)
        
        for root, dirs, files in os.walk("test_output"):
            pdf_files = [f for f in files if f.endswith('.pdf')]
            if pdf_files:
                rel_path = os.path.relpath(root, "test_output")
                print(f"\n {rel_path}:")
                for pdf in pdf_files[:5]:
                    print(f"   • {pdf}")
                if len(pdf_files) > 5:
                    print(f"   ... y {len(pdf_files) - 5} más")


def cleanup():
    """Limpia los archivos de prueba."""
    print("\n Limpiando archivos de prueba...")
    
    dirs_to_clean = ["test_output", "test_qrs"]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            import shutil
            shutil.rmtree(dir_path)
            print(f"    Eliminado: {dir_path}")
    
    print(" Limpieza completada")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Suite de pruebas para el generador de gafetes")
    parser.add_argument("--clean", action="store_true", help="Limpiar archivos de prueba")
    
    args = parser.parse_args()
    
    if args.clean:
        cleanup()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n Pruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"\n Error inesperado: {e}")
            
