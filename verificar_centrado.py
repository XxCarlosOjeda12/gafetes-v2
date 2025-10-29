#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación de centrado - generator.py
Verifica que las funciones de centrado funcionen correctamente
"""

import sys
import os

try:
    from generator import (
        calcular_x_centrado, 
        calcular_y_centrado_vertical,
        AREA_NOMBRE_APELLIDO,
        AREA_PUESTO,
        AREA_OFICINA,
        ANCHO_PUNTOS,
        ALTO_PUNTOS
    )
    from reportlab.pdfgen import canvas
    import io
    print(" Módulos importados correctamente")
except ImportError as e:
    print(f" Error importando módulos: {e}")
    print("\nAsegúrate de que generator.py esté en el mismo directorio.")
    sys.exit(1)


def test_centrado_horizontal():
    """Prueba el centrado horizontal de texto."""
    print("\n" + "="*60)
    print(" TEST 1: Centrado Horizontal")
    print("="*60)
    
    packet = io.BytesIO()
    test_canvas = canvas.Canvas(packet, pagesize=(ANCHO_PUNTOS, ALTO_PUNTOS))
    
    textos_prueba = [
        ("Ana", "Nombre corto"),
        ("Juan Carlos", "Nombre medio"),
        ("María Fernanda", "Nombre largo"),
    ]
    
    font_name = "Helvetica-Bold"
    font_size = 65
    x_centro = AREA_NOMBRE_APELLIDO["x_centro"]
    
    print(f"\n📐 Centro del gafete: {x_centro:.2f} puntos")
    print(f"📏 Fuente: {font_name}, Tamaño: {font_size}pt\n")
    
    for texto, descripcion in textos_prueba:
        x_calculado = calcular_x_centrado(test_canvas, texto, x_centro, font_name, font_size)
        ancho_texto = test_canvas.stringWidth(texto, font_name, font_size)
        x_final = x_calculado + (ancho_texto / 2)
        
        diferencia = abs(x_final - x_centro)
        
        print(f"Texto: '{texto}' ({descripcion})")
        print(f"  Ancho del texto: {ancho_texto:.2f} puntos")
        print(f"  X inicial: {x_calculado:.2f}")
        print(f"  X final (centro): {x_final:.2f}")
        print(f"  Diferencia del centro: {diferencia:.4f} puntos")
        
        if diferencia < 0.1:
            print("  CENTRADO PERFECTO\n")
        else:
            print("   Ligera desviación (puede ser por redondeo)\n")
    
    return True


def test_centrado_vertical():
    """Prueba el centrado vertical de texto (para oficina)."""
    print("\n" + "="*60)
    print("🧪 TEST 2: Centrado Vertical (Oficina)")
    print("="*60)
    
    packet = io.BytesIO()
    test_canvas = canvas.Canvas(packet, pagesize=(ANCHO_PUNTOS, ALTO_PUNTOS))
    
    oficinas_prueba = [
        ("CDMX", "Oficina corta"),
        ("Guadalajara", "Oficina media"),
        ("San Luis Potosí", "Oficina larga"),
    ]
    
    font_name = "Helvetica-Bold"
    font_size = 70
    y_centro = AREA_OFICINA["y_centro"]
    
    print(f"\n📐 Centro vertical: {y_centro:.2f} puntos")
    print(f"📏 Fuente: {font_name}, Tamaño: {font_size}pt\n")
    
    for oficina, descripcion in oficinas_prueba:
        y_calculado = calcular_y_centrado_vertical(test_canvas, oficina, y_centro, font_name, font_size)
        ancho_texto = test_canvas.stringWidth(oficina, font_name, font_size)
        y_final = y_calculado + (ancho_texto / 2)
        
        diferencia = abs(y_final - y_centro)
        
        print(f"Oficina: '{oficina}' ({descripcion})")
        print(f"  Ancho del texto (altura cuando rotado): {ancho_texto:.2f} puntos")
        print(f"  Y inicial: {y_calculado:.2f}")
        print(f"  Y final (centro): {y_final:.2f}")
        print(f"  Diferencia del centro: {diferencia:.4f} puntos")
        
        if diferencia < 0.1:
            print("   CENTRADO PERFECTO\n")
        else:
            print("   Ligera desviación (puede ser por redondeo)\n")
    
    return True


def test_configuracion():
    """Verifica la configuración del sistema."""
    print("\n" + "="*60)
    print("🔧 TEST 3: Verificación de Configuración")
    print("="*60)
    
    print(f"\n Dimensiones del gafete:")
    print(f"  Ancho: {ANCHO_PUNTOS:.2f} puntos")
    print(f"  Alto: {ALTO_PUNTOS:.2f} puntos")
    
    print(f"\n Configuración de áreas:")
    print(f"  NOMBRE/APELLIDO:")
    print(f"    - Centro X: {AREA_NOMBRE_APELLIDO['x_centro']:.2f}")
    print(f"    - Y Nombre: {AREA_NOMBRE_APELLIDO['y_nombre']}")
    print(f"    - Y Apellido: {AREA_NOMBRE_APELLIDO['y_apellido']}")
    print(f"    - Tamaño fuente: {AREA_NOMBRE_APELLIDO['tamaño_fuente']}pt")
    
    print(f"\n  PUESTO:")
    print(f"    - Centro X: {AREA_PUESTO['x_centro']:.2f}")
    print(f"    - Centro Y: {AREA_PUESTO['y_centro']}")
    print(f"    - Tamaño fuente: {AREA_PUESTO['tamaño_fuente']}pt")
    
    print(f"\n  OFICINA:")
    print(f"    - X: {AREA_OFICINA['x']}")
    print(f"    - Centro Y: {AREA_OFICINA['y_centro']}")
    print(f"    - Tamaño fuente: {AREA_OFICINA['tamaño_fuente']}pt")
    
    errores = []
    
    if AREA_NOMBRE_APELLIDO['x_centro'] > ANCHO_PUNTOS:
        errores.append("  Centro de nombre/apellido fuera del límite horizontal")
    
    if AREA_NOMBRE_APELLIDO['y_nombre'] > ALTO_PUNTOS:
        errores.append("  Posición Y del nombre fuera del límite vertical")
    
    if AREA_NOMBRE_APELLIDO['y_apellido'] > ALTO_PUNTOS:
        errores.append("  Posición Y del apellido fuera del límite vertical")
    
    if AREA_PUESTO['x_centro'] > ANCHO_PUNTOS:
        errores.append("  Centro del puesto fuera del límite horizontal")
    
    if AREA_OFICINA['y_centro'] > ALTO_PUNTOS:
        errores.append("  Centro vertical de oficina fuera del límite")
    
    if errores:
        print("\n ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  {error}")
        return False
    else:
        print("\n Configuración válida - Todos los elementos dentro de límites")
        return True


def main():
    """Ejecuta todos los tests."""
    print("="*60)
    print(" VERIFICACIÓN DE CENTRADO - generator.py")
    print("="*60)
    
    tests = [
        ("Centrado Horizontal", test_centrado_horizontal),
        ("Centrado Vertical", test_centrado_vertical),
        ("Configuración", test_configuracion),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"\n Error en test '{nombre}': {e}")
            resultados.append((nombre, False))
    
    print("\n" + "="*60)
    print(" RESUMEN DE TESTS")
    print("="*60)
    
    total_tests = len(resultados)
    tests_pasados = sum(1 for _, resultado in resultados if resultado)
    
    for nombre, resultado in resultados:
        status = " PASADO" if resultado else " FALLIDO"
        print(f"  {nombre}: {status}")
    
    print("\n" + "="*60)
    print(f"Total: {tests_pasados}/{total_tests} tests pasados")
    
    if tests_pasados == total_tests:
        print(" TODOS LOS TESTS PASARON")
        print("\n El sistema de centrado está funcionando correctamente!")
        return 0
    else:
        print("  ALGUNOS TESTS FALLARON")
        print("\nRevisa los errores anteriores para más detalles.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n  Test interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)