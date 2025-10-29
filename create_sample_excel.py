#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un archivo Excel de ejemplo para pruebas.
"""

import pandas as pd
import os

def create_sample_excel(filename="ejemplo_asistentes.xlsx"):
    """
    Crea un archivo Excel de ejemplo con el formato correcto.
    """
    
    data = {
        "Puesto": [
            "Director Regional",
            "Gerente de Eventos",
            "Coordinadora de Proyectos",
            "Subdirector",
            "Jefe de Área",
            "Analista Senior",
            "Director de Operaciones",
            "Gerente Comercial",
            "Supervisor de Calidad",
            "Coordinador Regional"
        ],
        "PrimerNombre": [
            "Juan",
            "María",
            "Ana",
            "Carlos",
            "Laura",
            "Pedro",
            "Sofía",
            "Miguel",
            "Carmen",
            "Roberto"
        ],
        "PrimerApellido": [
            "García",
            "Rodríguez",
            "Martínez",
            "López",
            "Hernández",
            "González",
            "Ramírez",
            "Torres",
            "Flores",
            "Rivera"
        ],
        "Oficina": [
            "CDMX",
            "Guadalajara",
            "Monterrey",
            "Puebla",
            "CDMX",
            "Querétaro",
            "Tijuana",
            "Mérida",
            "CDMX",
            "Guadalajara"
        ],
        "Tour": [
            "Por el Centro Histórico",
            "Museando Ando",
            "Vamos Pa'l Mercado",
            "Colores de México",
            "Por el Centro Histórico",
            "Museando Ando",
            "Colores de México",
            "Vamos Pa'l Mercado",
            "Por el Centro Histórico",
            "Museando Ando"
        ],
        "Mesa": [
            "Valuación",
            "Grúas",
            "Q Salud",
            "Proyectos estratégicos",
            "Productos y Tarifas",
            "Verificaciones",
            "Valuación",
            "Grúas",
            "Q Salud",
            "Proyectos estratégicos"
        ],
        "LLevaConyugue": [
            "SI",
            "NO",
            "SI",
            "NO",
            "SI",
            "NO",
            "NO",
            "SI",
            "NO",
            "SI"
        ],
        "PrimerNombreConyugue": [
            "Elena",
            "",
            "Luis",
            "",
            "Patricia",
            "",
            "",
            "Andrea",
            "",
            "Diana"
        ],
        "PrimerApellidoConyugue": [
            "Mendoza",
            "",
            "Sánchez",
            "",
            "Vargas",
            "",
            "",
            "Morales",
            "",
            "Castro"
        ],
        "QR": [
            "QR001",
            "QR002",
            "QR003",
            "QR004",
            "QR005",
            "QR006",
            "QR007",
            "QR008",
            "QR009",
            "QR010"
        ],
        "QR_Conyugue": [
            "QRC001",
            "",
            "QRC003",
            "",
            "QRC005",
            "",
            "",
            "QRC008",
            "",
            "QRC010"
        ]
    }
    
    df = pd.DataFrame(data)
    
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f" Archivo Excel de ejemplo creado: {filename}")
    print(f"   • {len(df)} asistentes")
    print(f"   • {sum(df['LLevaConyugue'] == 'SI')} con acompañante")
    print(f"   • {sum(df['LLevaConyugue'] == 'NO')} sin acompañante")
    
    return filename


def create_invalid_excel(filename="ejemplo_invalido.xlsx"):
    """
    Crea un archivo Excel con columnas faltantes para probar validación.
    """
    
    data = {
        "Puesto": ["Director"],
        "PrimerNombre": ["Juan"],
        "PrimerApellido": ["García"],
        "Oficina": ["CDMX"],
        "Tour": ["Por el Centro Histórico"],
        "Mesa": ["Valuación"],
        "LLevaConyugue": ["NO"],
        "PrimerNombreConyugue": [""],
        "PrimerApellidoConyugue": [""],
        "QR": ["QR001"]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f" Archivo Excel inválido creado: {filename}")
    print("   (Falta columna QR_Conyugue para probar validación)")
    
    return filename


if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR DE ARCHIVOS EXCEL DE EJEMPLO")
    print("=" * 60)
    
    os.makedirs("ejemplos", exist_ok=True)
    
    valid_file = create_sample_excel("ejemplos/ejemplo_asistentes.xlsx")
    
    invalid_file = create_invalid_excel("ejemplos/ejemplo_invalido.xlsx")
    
    print("\n" + "=" * 60)
    print("CÓMO USAR LOS ARCHIVOS DE EJEMPLO:")
    print("=" * 60)
    
    print("\n1. Para probar con el archivo válido:")
    print(f"   python gafetes_generator.py --excel {valid_file}")
    
    print("\n2. Para probar con caché de QRs:")
    print(f"   python gafetes_generator.py --excel {valid_file} --qr-strategy cache")
    
    print("\n3. Para probar modo dry-run:")
    print(f"   python gafetes_generator.py --excel {valid_file} --dry-run")
    
    print("\n4. Para probar validación (debe fallar):")
    print(f"   python gafetes_generator.py --excel {invalid_file}")
    
    print("\n5. Para probar con debug:")
    print(f"   python gafetes_generator.py --excel {valid_file} --debug --log-level DEBUG")
