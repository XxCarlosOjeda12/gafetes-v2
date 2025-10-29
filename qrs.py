#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para manejo de códigos QR: descarga, caché y generación local.
"""

import io
import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import qrcode
from PIL import Image

logger = logging.getLogger(__name__)

QR_BASE_URL = "https://evento-directores.qualitaseventos.mx/downloadQr/{codigo}/"
DOWNLOAD_TIMEOUT = 10
MAX_RETRIES = 2
RETRY_DELAY = 1

QR_BOX_SIZE = 10
QR_BORDER = 4
QR_DEFAULT_SIZE = (200, 200)


def generate_qr_local(data: str, size: tuple = QR_DEFAULT_SIZE) -> io.BytesIO:
    """
    Genera un código QR localmente como fallback.
    
    Args:
        data: Datos a codificar en el QR
        size: Tamaño del QR en pixeles (ancho, alto)
        
    Returns:
        BytesIO con la imagen del QR
    """
    logger.info(f"Generando QR localmente para: {data[:50]}...")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if img.size != size:
        img = img.resize(size, Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def download_qr_from_url(url: str, retries: int = MAX_RETRIES) -> Optional[bytes]:
    """
    Descarga un QR desde una URL con reintentos.
    
    Args:
        url: URL de descarga
        retries: Número de reintentos
        
    Returns:
        Bytes de la imagen o None si falla
    """
    for attempt in range(retries):
        try:
            logger.debug(f"Intento {attempt + 1}/{retries}: Descargando {url}")
            
            response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type and len(response.content) > 0:
                logger.warning(f"Respuesta no es imagen: {content_type}")
                
            return response.content
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout descargando {url} (intento {attempt + 1})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error descargando {url}: {e}")
        
        if attempt < retries - 1:
            time.sleep(RETRY_DELAY)
    
    return None


def get_qr_image(
    qr_code_or_path: str,
    strategy: Literal["download", "cache"] = "download",
    qrs_dir: str = "qrs",
    allow_fallback: bool = False
) -> io.BytesIO:
    """
    Obtiene una imagen QR según la estrategia configurada.
    
    Args:
        qr_code_or_path: Código QR, URL o ruta a archivo local
        strategy: "download" (no guardar) o "cache" (guardar localmente)
        qrs_dir: Directorio para caché de QRs
        allow_fallback: Si permitir generación local como fallback (default: False)
        
    Returns:
        BytesIO con la imagen del QR
        
    Raises:
        Exception: Si no se puede obtener el QR del servidor
    """
    if os.path.isfile(qr_code_or_path):
        logger.info(f"Usando QR local: {qr_code_or_path}")
        with open(qr_code_or_path, 'rb') as f:
            return io.BytesIO(f.read())
    
    if qr_code_or_path.startswith('http://') or qr_code_or_path.startswith('https://'):
        url = qr_code_or_path
        if '/downloadQr/' in url:
            codigo = url.split('/downloadQr/')[-1].rstrip('/')
        else:
            codigo = qr_code_or_path.replace('/', '_').replace(':', '')
    else:
        codigo = qr_code_or_path
        url = QR_BASE_URL.format(codigo=codigo)
    
    if strategy == "cache":
        os.makedirs(qrs_dir, exist_ok=True)
        cache_path = os.path.join(qrs_dir, f"{codigo}.png")
        
        if os.path.exists(cache_path):
            if not cache_path.endswith("_local.png"):
                logger.info(f"Usando QR desde caché: {cache_path}")
                with open(cache_path, 'rb') as f:
                    return io.BytesIO(f.read())
            else:
                logger.warning(f"QR en caché es local, intentando descargar del servidor nuevamente")
    
    logger.info(f"Descargando QR desde: {url}")
    qr_bytes = download_qr_from_url(url)
    
    if qr_bytes:
        logger.info(f"QR descargado exitosamente ({len(qr_bytes)} bytes)")
        
        if strategy == "cache":
            cache_path = os.path.join(qrs_dir, f"{codigo}.png")
            with open(cache_path, 'wb') as f:
                f.write(qr_bytes)
            logger.info(f"QR guardado en caché: {cache_path}")
        
        return io.BytesIO(qr_bytes)
    
    if not allow_fallback:
        error_msg = (
            f" ERROR CRÍTICO: No se pudo descargar el QR del servidor para código '{codigo}'. "
            f"Este QR es necesario para el escaneo en el evento. "
            f"Por favor verifica tu conexión a internet y que el servidor esté disponible."
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.warning(f" ATENCIÓN: Generando QR local para '{qr_code_or_path}'. "
                  f"Este QR NO funcionará para el escaneo en el evento.")
    qr_buffer = generate_qr_local(qr_code_or_path)
    
    if strategy == "cache":
        cache_path = os.path.join(qrs_dir, f"{codigo}_local.png")
        qr_buffer.seek(0)
        with open(cache_path, 'wb') as f:
            f.write(qr_buffer.read())
        qr_buffer.seek(0)
        logger.warning(f"QR local guardado en caché (NO VÁLIDO PARA EVENTO): {cache_path}")
    
    return qr_buffer


def prefetch_qrs(
    codes: List[str],
    strategy: Literal["download", "cache"] = "cache",
    qrs_dir: str = "qrs",
    workers: int = 8,
    allow_fallback: bool = False
) -> Dict[str, Union[io.BytesIO, str]]:
    """
    Descarga múltiples QRs en paralelo.
    
    Args:
        codes: Lista de códigos QR
        strategy: Estrategia de descarga
        qrs_dir: Directorio para caché
        workers: Número de threads para descarga paralela
        allow_fallback: Si permitir generación local como fallback
        
    Returns:
        Diccionario {código: BytesIO o mensaje de error}
    """
    logger.info(f"Pre-descargando {len(codes)} QRs con {workers} workers...")
    
    results = {}
    
    def fetch_single(code):
        try:
            qr_buffer = get_qr_image(code, strategy, qrs_dir, allow_fallback)
            return (code, qr_buffer)
        except Exception as e:
            logger.error(f"Error obteniendo QR {code}: {e}")
            return (code, str(e))
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_single, code): code for code in codes}
        
        for future in as_completed(futures):
            code, result = future.result()
            results[code] = result
            
            if isinstance(result, io.BytesIO):
                logger.debug(f" QR obtenido: {code}")
            else:
                logger.warning(f" QR fallido: {code} - {result}")
    
    success = sum(1 for r in results.values() if isinstance(r, io.BytesIO))
    failed = len(codes) - success
    logger.info(f"Pre-descarga completada: {success}/{len(codes)} exitosos")
    
    if failed > 0 and not allow_fallback:
        logger.error(f" {failed} QRs no pudieron ser descargados del servidor. "
                    f"Estos gafetes NO tendrán QRs válidos para el evento.")
    
    return results


def clean_cache(qrs_dir: str = "qrs", max_age_days: int = 30) -> int:
    """
    Limpia QRs antiguos del caché.
    
    Args:
        qrs_dir: Directorio de caché
        max_age_days: Edad máxima en días
        
    Returns:
        Número de archivos eliminados
    """
    if not os.path.exists(qrs_dir):
        return 0
    
    deleted = 0
    max_age_seconds = max_age_days * 24 * 60 * 60
    current_time = time.time()
    
    for file_path in Path(qrs_dir).glob("*.png"):
        file_age = current_time - file_path.stat().st_mtime
        
        if file_age > max_age_seconds:
            try:
                file_path.unlink()
                deleted += 1
                logger.debug(f"Eliminado QR antiguo: {file_path}")
            except Exception as e:
                logger.warning(f"Error eliminando {file_path}: {e}")
    
    if deleted > 0:
        logger.info(f"Limpieza de caché: {deleted} archivos eliminados")
    
    return deleted


if __name__ == "__main__":
    import sys
    
    print("=== Prueba del módulo QRs ===\n")
    
    print("1. Generando QR local...")
    qr_local = generate_qr_local("https://example.com/test")
    print(f"    QR generado: {len(qr_local.getvalue())} bytes\n")
    
    test_code = "TEST123"
    
    print("2. Probando estrategia 'download'...")
    try:
        qr_download = get_qr_image(test_code, strategy="download")
        print(f"    QR obtenido: {len(qr_download.getvalue())} bytes\n")
    except Exception as e:
        print(f"    Error: {e}\n")
    
    print("3. Probando estrategia 'cache'...")
    try:
        qr_cache = get_qr_image(test_code, strategy="cache", qrs_dir="test_qrs")
        print(f"    QR obtenido: {len(qr_cache.getvalue())} bytes")
        
        if os.path.exists(f"test_qrs/{test_code}.png") or os.path.exists(f"test_qrs/{test_code}_local.png"):
            print("    QR guardado en caché\n")
        
    except Exception as e:
        print(f"    Error: {e}\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--prefetch":
        print("4. Probando prefetch de múltiples QRs...")
        test_codes = [f"CODE{i}" for i in range(5)]
        results = prefetch_qrs(test_codes, strategy="cache", qrs_dir="test_qrs", workers=3)
        
        for code, result in results.items():
            if isinstance(result, io.BytesIO):
                print(f"    {code}: {len(result.getvalue())} bytes")
            else:
                print(f"    {code}: {result}")
    
    print("\n=== Pruebas completadas ===")
