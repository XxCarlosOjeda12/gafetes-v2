#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para lectura y validación de archivos Excel con datos de asistentes.
"""

import logging
from typing import List, Dict, Optional, Set
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
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


def normalize_column_name(col: str) -> str:
    """
    Normaliza el nombre de una columna removiendo espacios extremos y 
    convirtiendo a formato consistente.
    
    Args:
        col: Nombre de columna a normalizar
        
    Returns:
        Nombre normalizado
    """
    return col.strip()


def validate_columns(headers: List[str]) -> None:
    """
    Valida que todas las columnas requeridas estén presentes en los headers.
    
    Args:
        headers: Lista de nombres de columnas del Excel
        
    Raises:
        ValueError: Si faltan columnas requeridas
    """
    normalized_headers = {normalize_column_name(h) for h in headers}
    
    missing_columns = []
    for required_col in REQUIRED_COLUMNS:
        found = False
        for header in normalized_headers:
            if header.upper() == required_col.upper():
                found = True
                break
        if not found:
            missing_columns.append(required_col)
    
    if missing_columns:
        raise ValueError(
            f"Faltan las siguientes columnas requeridas: {', '.join(missing_columns)}. "
            f"Columnas encontradas: {', '.join(headers)}"
        )


def parse_boolean(value) -> bool:
    """
    Convierte un valor a booleano según las reglas definidas.
    
    Args:
        value: Valor a convertir
        
    Returns:
        True si el valor está en TRUE_VALUES, False en caso contrario
    """
    if pd.isna(value):
        return False
    
    str_value = str(value).strip().upper()
    return str_value in TRUE_VALUES


def validate_row(row: Dict, row_index: int) -> Optional[str]:
    """
    Valida una fila del Excel y retorna mensaje de error si hay problemas.
    
    Args:
        row: Diccionario con los datos de la fila
        row_index: Índice de la fila (para mensajes de error)
        
    Returns:
        Mensaje de error si la fila es inválida, None si es válida
    """
    errors = []
    
    if not row.get("PrimerNombre") or pd.isna(row["PrimerNombre"]):
        errors.append("PrimerNombre vacío")
    
    if not row.get("PrimerApellido") or pd.isna(row["PrimerApellido"]):
        errors.append("PrimerApellido vacío")
    
    if not row.get("QR") or pd.isna(row["QR"]):
        errors.append("QR vacío")
    
    if row.get("LLevaConyugue"):
        if not row.get("PrimerNombreConyugue") or pd.isna(row["PrimerNombreConyugue"]):
            errors.append("LLevaConyugue=True pero PrimerNombreConyugue vacío")
        
        if not row.get("PrimerApellidoConyugue") or pd.isna(row["PrimerApellidoConyugue"]):
            errors.append("LLevaConyugue=True pero PrimerApellidoConyugue vacío")
        
        if not row.get("QR_Conyugue") or pd.isna(row["QR_Conyugue"]):
            errors.append("LLevaConyugue=True pero QR_Conyugue vacío")
    
    if errors:
        return f"Fila {row_index + 2}: {'; '.join(errors)}"   
    
    return None


def read_attendees(excel_path: str, sheet_name: Optional[str] = None) -> List[Dict]:
    """
    Lee un archivo Excel y retorna lista de asistentes con validación estricta.
    
    Args:
        excel_path: Ruta al archivo Excel
        sheet_name: Nombre de la hoja a leer (opcional, por defecto la primera)
        
    Returns:
        Lista de diccionarios con los datos de cada asistente válido
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si faltan columnas requeridas o el formato es inválido
        Exception: Para otros errores de lectura
    """
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {excel_path}")
    
    logger.info(f"Leyendo archivo Excel: {excel_path}")
    
    try:
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, keep_default_na=False, na_values=[''])
            logger.info(f"Usando hoja: {sheet_name}")
        else:
            df = pd.read_excel(excel_path, keep_default_na=False, na_values=[''])   
            logger.info(f"Usando primera hoja del archivo")
        
        validate_columns(df.columns.tolist())
        
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        column_mapping = {}
        for df_col in df.columns:
            for req_col in REQUIRED_COLUMNS:
                if df_col.upper() == req_col.upper():
                    column_mapping[df_col] = req_col
                    break
        
        df = df.rename(columns=column_mapping)
        
        attendees = []
        invalid_rows = []
        
        for idx, row in df.iterrows():
            entry = {
                "Puesto": str(row["Puesto"]) if not pd.isna(row["Puesto"]) else "",
                "PrimerNombre": str(row["PrimerNombre"]) if not pd.isna(row["PrimerNombre"]) else "",
                "PrimerApellido": str(row["PrimerApellido"]) if not pd.isna(row["PrimerApellido"]) else "",
                "Oficina": str(row["Oficina"]) if not pd.isna(row["Oficina"]) else "",
                "Tour": str(row["Tour"]) if not pd.isna(row["Tour"]) else "",
                "Mesa": str(row["Mesa"]) if not pd.isna(row["Mesa"]) else "",
                "LLevaConyugue": parse_boolean(row["LLevaConyugue"]),
                "PrimerNombreConyugue": str(row["PrimerNombreConyugue"]) if not pd.isna(row["PrimerNombreConyugue"]) else "",
                "PrimerApellidoConyugue": str(row["PrimerApellidoConyugue"]) if not pd.isna(row["PrimerApellidoConyugue"]) else "",
                "QR": str(row["QR"]) if not pd.isna(row["QR"]) else "",
                "QR_Conyugue": str(row["QR_Conyugue"]) if not pd.isna(row["QR_Conyugue"]) else ""
            }
            
            error_msg = validate_row(entry, idx)
            if error_msg:
                invalid_rows.append(error_msg)
                logger.warning(error_msg)
            else:
                attendees.append(entry)
        
        logger.info(f"Total filas procesadas: {len(df)}")
        logger.info(f"Filas válidas: {len(attendees)}")
        logger.info(f"Filas inválidas: {len(invalid_rows)}")
        
        if invalid_rows:
            logger.warning(f"Filas omitidas por errores de validación:")
            for msg in invalid_rows[:5]:
                logger.warning(f"  - {msg}")
            if len(invalid_rows) > 5:
                logger.warning(f"  ... y {len(invalid_rows) - 5} más")
        
        return attendees
        
    except FileNotFoundError:
        raise
    except ValueError:
        raise  
    except Exception as e:
        raise Exception(f"Error leyendo el archivo Excel: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            attendees = read_attendees(sys.argv[1])
            print(f"\n Lectura exitosa: {len(attendees)} asistentes encontrados")
            
            if attendees:
                print("\nPrimer asistente:")
                for key, value in attendees[0].items():
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"\n Error: {e}")
    else:
        print("Uso: python excel.py <archivo.xlsx>")
