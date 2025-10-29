#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalación y configuración inicial del Generador de Gafetes.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Imprime un encabezado formateado."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")

def print_success(text):
    """Imprime un mensaje de éxito."""
    print(f"{Colors.OKGREEN} {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime una advertencia."""
    print(f"{Colors.WARNING} {text}{Colors.ENDC}")

def print_error(text):
    """Imprime un error."""
    print(f"{Colors.FAIL} {text}{Colors.ENDC}")

def print_info(text):
    """Imprime información."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def check_python_version():
    """Verifica la versión de Python."""
    print("\n📐 Verificando versión de Python...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3:
        print_error(f"Python {version_str} detectado. Se requiere Python 3.7+")
        return False
    
    if version.major == 3 and version.minor < 7:
        print_warning(f"Python {version_str} detectado. Se recomienda Python 3.7+")
        return True
    
    print_success(f"Python {version_str} ✓")
    return True

def check_pip():
    """Verifica que pip esté instalado."""
    print("\n Verificando pip...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"pip instalado: {result.stdout.strip()}")
            return True
        else:
            print_error("pip no está instalado")
            print_info("Instala pip con: python -m ensurepip --upgrade")
            return False
    except Exception as e:
        print_error(f"Error verificando pip: {e}")
        return False

def install_requirements():
    """Instala las dependencias del proyecto."""
    print("\n Instalando dependencias...")
    
    if not os.path.exists("requirements.txt"):
        print_error("No se encuentra requirements.txt")
        return False
    
    try:
        print_info("Ejecutando: pip install -r requirements.txt")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Dependencias instaladas correctamente")
            
            installed = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                     capture_output=True, text=True)
            
            required_packages = ["pypdf", "reportlab", "Pillow", "qrcode", "pandas", "openpyxl", "requests"]
            print("\n Paquetes verificados:")
            
            for package in required_packages:
                if package.lower() in installed.stdout.lower():
                    print(f"   ✓ {package}")
                else:
                    print_warning(f"   ✗ {package} - puede requerir instalación manual")
            
            return True
        else:
            print_error("Error instalando dependencias")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Error ejecutando pip: {e}")
        return False

def create_directories():
    """Crea los directorios necesarios."""
    print("\n Creando estructura de directorios...")
    
    directories = [
        "gafetes",
        "qrs",
        "logs",
        "ejemplos",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✓ {directory}/")
    
    print_success("Directorios creados")
    return True

def check_templates():
    """Verifica la existencia de templates."""
    print("\n Verificando templates...")
    
    templates = {
        "template_frente.pdf": "Plantilla para el frente del gafete",
        "template_reverso.pdf": "Plantilla para el reverso del gafete"
    }
    
    missing = []
    for template, description in templates.items():
        if os.path.exists(template):
            print(f"    {template}")
        else:
            print_warning(f"    {template} - {description}")
            missing.append(template)
    
    if missing:
        print_warning(f"\nFaltan {len(missing)} templates. Colócalos en el directorio del proyecto.")
        return False
    
    print_success("Todos los templates encontrados")
    return True

def check_modules():
    """Verifica que todos los módulos del proyecto estén presentes."""
    print("\n Verificando módulos del proyecto...")
    
    modules = [
        "gafetes_generator.py",
        "cli.py",
        "excel.py",
        "qrs.py",
        "generator.py",
        "utils.py",
        "config.py"
    ]
    
    missing = []
    for module in modules:
        if os.path.exists(module):
            print(f"   ✓ {module}")
        else:
            print_error(f"   ✗ {module}")
            missing.append(module)
    
    if missing:
        print_error(f"Faltan {len(missing)} módulos")
        return False
    
    print_success("Todos los módulos encontrados")
    return True

def create_example_excel():
    """Crea el archivo Excel de ejemplo."""
    print("\n Generando archivo Excel de ejemplo...")
    
    try:
        result = subprocess.run([sys.executable, "create_sample_excel.py"],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Archivos de ejemplo creados en ejemplos/")
            return True
        else:
            print_warning("No se pudo crear el Excel de ejemplo automáticamente")
            print_info("Puedes crearlo manualmente con: python create_sample_excel.py")
            return False
    except Exception as e:
        print_warning(f"Error creando ejemplo: {e}")
        return False

def test_import():
    """Prueba importar los módulos principales."""
    print("\n Probando imports...")
    
    modules_to_test = [
        ("excel", "Módulo de lectura de Excel"),
        ("qrs", "Módulo de gestión de QRs"),
        ("generator", "Módulo de generación de PDFs"),
        ("utils", "Módulo de utilidades"),
        ("cli", "Módulo CLI"),
        ("config", "Módulo de configuración")
    ]
    
    all_ok = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"   ✓ {module_name}: {description}")
        except ImportError as e:
            print_error(f"    {module_name}: {e}")
            all_ok = False
        except Exception as e:
            print_warning(f"    {module_name}: {e}")
            all_ok = False
    
    if all_ok:
        print_success("Todos los módulos se pueden importar")
    
    return all_ok

def run_test():
    """Ejecuta una prueba básica del sistema."""
    print("\n Ejecutando prueba básica...")
    
    if not os.path.exists("ejemplos/ejemplo_asistentes.xlsx"):
        print_warning("No existe archivo de ejemplo. Creándolo...")
        create_example_excel()
    
    print_info("Ejecutando: python gafetes_generator.py --excel ejemplos/ejemplo_asistentes.xlsx --dry-run")
    
    try:
        result = subprocess.run([sys.executable, "gafetes_generator.py", 
                               "--excel", "ejemplos/ejemplo_asistentes.xlsx", 
                               "--dry-run"],
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("Prueba completada exitosamente")
            if "asistentes encontrados" in result.stdout:
                print_info("El sistema puede leer y validar archivos Excel correctamente")
            return True
        else:
            print_error("La prueba falló")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_error("La prueba tardó demasiado tiempo")
        return False
    except Exception as e:
        print_error(f"Error ejecutando prueba: {e}")
        return False

def show_next_steps():
    """Muestra los siguientes pasos."""
    print_header("SIGUIENTES PASOS")
    
    print(f"\n{Colors.BOLD}1. Si faltan templates:{Colors.ENDC}")
    print("   Coloca template_frente.pdf y template_reverso.pdf en el directorio del proyecto")
    
    print(f"\n{Colors.BOLD}2. Prepara tu archivo Excel con las columnas:{Colors.ENDC}")
    columns = [
        "Puesto", "PrimerNombre", "PrimerApellido", "Oficina", "Tour", "Mesa",
        "LLevaConyugue", "PrimerNombreConyugue", "PrimerApellidoConyugue", "QR", "QR_Conyugue"
    ]
    for col in columns:
        print(f"   • {col}")
    
    print(f"\n{Colors.BOLD}3. Ejecuta el generador:{Colors.ENDC}")
    print("   python gafetes_generator.py --excel tu_archivo.xlsx")
    
    print(f"\n{Colors.BOLD}4. Opciones útiles:{Colors.ENDC}")
    print("   --dry-run         : Solo validar sin generar")
    print("   --qr-strategy cache : Guardar QRs descargados")
    print("   --debug          : Generar PDFs de debug")
    print("   --help           : Ver todas las opciones")
    
    print(f"\n{Colors.BOLD}5. Para más información:{Colors.ENDC}")
    print("   Consulta README.md")

def main():
    """Función principal del instalador."""
    print_header("INSTALADOR - GENERADOR DE GAFETES v2.0.0")
    
    print(f"\n Sistema: {platform.system()} {platform.release()}")
    print(f" Arquitectura: {platform.machine()}")
    
    checks = {
        "Python": check_python_version(),
        "pip": check_pip(),
        "Módulos": check_modules()
    }
    
    if checks["pip"]:
        checks["Dependencias"] = install_requirements()
    else:
        print_warning("Saltando instalación de dependencias (pip no disponible)")
    
    checks["Directorios"] = create_directories()
    
    checks["Templates"] = check_templates()
    
    if checks.get("Dependencias", False):
        checks["Imports"] = test_import()
    
    create_example_excel()
    
    print_header("RESUMEN DE INSTALACIÓN")
    
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    for component, status in checks.items():
        if status:
            print(f"    {component}")
        else:
            print(f"    {component}")
    
    print(f"\n{Colors.BOLD}Estado: {passed}/{total} componentes configurados{Colors.ENDC}")
    
    if passed == total:
        print_success("\n¡Instalación completada exitosamente!")
        
        print("\n" + "=" * 70)
        if run_test():
            print_success("\n ¡El sistema está listo para usar!")
        else:
            print_warning("\nLa prueba falló, pero puedes intentar ejecutar el sistema manualmente")
    else:
        print_warning("\nInstalación incompleta. Revisa los componentes faltantes.")
    
    show_next_steps()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)
