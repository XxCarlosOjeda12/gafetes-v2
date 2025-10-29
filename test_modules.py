#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitarios para los módulos del generador de gafetes.
"""

import unittest
import os
import sys
import io
import tempfile
from pathlib import Path
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import excel
import qrs
import utils
import config


class TestExcelModule(unittest.TestCase):
    """Tests para el módulo excel.py"""
    
    def setUp(self):
        """Preparar datos de prueba."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.xlsx")
        
    def tearDown(self):
        """Limpiar archivos temporales."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_columns_valid(self):
        """Test: validación de columnas correctas."""
        headers = [
            "Puesto", "PrimerNombre", "PrimerApellido", "Oficina",
            "Tour", "Mesa", "LLevaConyugue", "PrimerNombreConyugue",
            "PrimerApellidoConyugue", "QR", "QR_Conyugue"
        ]
        
        try:
            excel.validate_columns(headers)
            self.assertTrue(True)
        except ValueError:
            self.fail("validate_columns lanzó ValueError con columnas válidas")
    
    def test_validate_columns_missing(self):
        """Test: detección de columnas faltantes."""
        headers = ["Puesto", "PrimerNombre"]
        
        with self.assertRaises(ValueError) as context:
            excel.validate_columns(headers)
        
        self.assertIn("Faltan las siguientes columnas", str(context.exception))
    
    def test_parse_boolean(self):
        """Test: conversión de valores a booleano."""
        true_values = ["SI", "sí", "S", "YES", "y", "1", "TRUE", "VERDADERO"]
        for value in true_values:
            self.assertTrue(excel.parse_boolean(value), f"'{value}' debería ser True")
        
        false_values = ["NO", "n", "0", "FALSE", "", None]
        for value in false_values:
            self.assertFalse(excel.parse_boolean(value), f"'{value}' debería ser False")
    
    def test_normalize_column_name(self):
        """Test: normalización de nombres de columna."""
        self.assertEqual(excel.normalize_column_name("  Puesto  "), "Puesto")
        self.assertEqual(excel.normalize_column_name("PrimerNombre"), "PrimerNombre")
        self.assertEqual(excel.normalize_column_name(" QR "), "QR")
    
    def test_read_attendees_valid_file(self):
        """Test: lectura de archivo Excel válido."""
        data = {
            "Puesto": ["Director"],
            "PrimerNombre": ["Juan"],
            "PrimerApellido": ["García"],
            "Oficina": ["CDMX"],
            "Tour": ["Por el Centro Histórico"],
            "Mesa": ["Valuación"],
            "LLevaConyugue": ["SI"],
            "PrimerNombreConyugue": ["María"],
            "PrimerApellidoConyugue": ["López"],
            "QR": ["QR001"],
            "QR_Conyugue": ["QR002"]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(self.test_file, index=False)
        
        attendees = excel.read_attendees(self.test_file)
        
        self.assertEqual(len(attendees), 1)
        self.assertEqual(attendees[0]["PrimerNombre"], "Juan")
        self.assertEqual(attendees[0]["PrimerApellido"], "García")
        self.assertTrue(attendees[0]["LLevaConyugue"])
    
    def test_read_attendees_file_not_found(self):
        """Test: archivo no encontrado."""
        with self.assertRaises(FileNotFoundError):
            excel.read_attendees("archivo_inexistente.xlsx")


class TestQRsModule(unittest.TestCase):
    """Tests para el módulo qrs.py"""
    
    def setUp(self):
        """Preparar directorio temporal."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpiar archivos temporales."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_generate_qr_local(self):
        """Test: generación local de código QR."""
        data = "https://example.com/test"
        qr_buffer = qrs.generate_qr_local(data)
        
        self.assertIsInstance(qr_buffer, io.BytesIO)
        self.assertGreater(len(qr_buffer.getvalue()), 0)
    
    def test_get_qr_image_local_file(self):
        """Test: obtener QR desde archivo local."""
        test_qr_path = os.path.join(self.test_dir, "test.png")
        qr_buffer = qrs.generate_qr_local("TEST")
        
        with open(test_qr_path, 'wb') as f:
            f.write(qr_buffer.getvalue())
        
        result = qrs.get_qr_image(test_qr_path)
        
        self.assertIsInstance(result, io.BytesIO)
        self.assertGreater(len(result.getvalue()), 0)
    
    def test_clean_cache(self):
        """Test: limpieza de caché."""
        for i in range(3):
            Path(self.test_dir, f"qr_{i}.png").touch()
        
        deleted = qrs.clean_cache(self.test_dir, max_age_days=0)
        
        self.assertEqual(deleted, 3)


class TestUtilsModule(unittest.TestCase):
    """Tests para el módulo utils.py"""
    
    def test_sanitizar_nombre_archivo(self):
        """Test: sanitización de nombres de archivo."""
        tests = [
            ("Juan García", "Juan_García"),
            ("María José/López", "María_JoséLópez"),
            ("Test@#$%123", "Test123"),
            ("   espacios   múltiples   ", "espacios_múltiples"),
            ("", "sin_nombre"),
            (None, "sin_nombre")
        ]
        
        for input_val, expected in tests:
            if input_val is None:
                result = utils.sanitizar_nombre_archivo("")
            else:
                result = utils.sanitizar_nombre_archivo(input_val)
            self.assertEqual(result, expected, f"'{input_val}' -> '{result}' != '{expected}'")
    
    def test_normalizar_string(self):
        """Test: normalización de strings."""
        tests = [
            ("  texto  con   espacios  ", "texto con espacios"),
            ("", ""),
            ("Normal", "Normal"),
            ("Con\nmúltiples\nlíneas", "Con múltiples líneas")
        ]
        
        for input_val, expected in tests:
            result = utils.normalizar_string(input_val)
            self.assertEqual(result, expected)
    
    def test_generator_stats(self):
        """Test: sistema de estadísticas."""
        stats = utils.GeneratorStats()
        
        stats.filas_procesadas = 10
        stats.gafetes_titulares = 8
        stats.gafetes_acompanantes = 3
        stats.filas_omitidas = 2
        
        resumen = stats.generar_resumen()
        
        self.assertIn("10", resumen)
        self.assertIn("8", resumen)
        self.assertIn("3", resumen)
        self.assertIn("2", resumen)
    
    def test_formato_tabla(self):
        """Test: formato de tabla ASCII."""
        headers = ["Col1", "Col2"]
        rows = [["A", "B"], ["C", "D"]]
        
        table = utils.formato_tabla(headers, rows)
        
        self.assertIn("Col1", table)
        self.assertIn("Col2", table)
        self.assertIn("A", table)
        self.assertIn("D", table)
        self.assertIn("+", table)
        self.assertIn("|", table)


class TestConfigModule(unittest.TestCase):
    """Tests para el módulo config.py"""
    
    def test_constants_defined(self):
        """Test: constantes importantes definidas."""
        self.assertTrue(hasattr(config, 'PAGE_WIDTH_MM'))
        self.assertTrue(hasattr(config, 'PAGE_HEIGHT_MM'))
        self.assertTrue(hasattr(config, 'EXCEL_REQUIRED_COLUMNS'))
        self.assertTrue(hasattr(config, 'MESAS_VALIDAS'))
        self.assertTrue(hasattr(config, 'PASEOS_VALIDOS'))
        self.assertTrue(hasattr(config, 'QR_BASE_URL'))
    
    def test_page_dimensions(self):
        """Test: dimensiones de página correctas."""
        self.assertEqual(config.PAGE_WIDTH_MM, 281)
        self.assertEqual(config.PAGE_HEIGHT_MM, 453)
        self.assertAlmostEqual(config.PAGE_WIDTH_POINTS, 796.5, places=1)
        self.assertAlmostEqual(config.PAGE_HEIGHT_POINTS, 1283.5, places=1)
    
    def test_required_columns(self):
        """Test: columnas requeridas definidas."""
        expected_columns = [
            "Puesto", "PrimerNombre", "PrimerApellido", "Oficina",
            "Tour", "Mesa", "LLevaConyugue", "PrimerNombreConyugue",
            "PrimerApellidoConyugue", "QR", "QR_Conyugue"
        ]
        
        self.assertEqual(config.EXCEL_REQUIRED_COLUMNS, expected_columns)
    
    def test_get_font_path(self):
        """Test: obtención de ruta de fuente."""
        font = config.get_font_path()
        
        self.assertIsNotNone(font)
        self.assertTrue(len(font) > 0)


class TestIntegration(unittest.TestCase):
    """Tests de integración entre módulos."""
    
    def setUp(self):
        """Preparar entorno de prueba."""
        self.test_dir = tempfile.mkdtemp()
        self.excel_file = os.path.join(self.test_dir, "test_integration.xlsx")
        
    def tearDown(self):
        """Limpiar archivos temporales."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_excel_to_qr_flow(self):
        """Test: flujo de Excel a generación de QR."""
        data = {
            "Puesto": ["Director", "Gerente"],
            "PrimerNombre": ["Juan", "María"],
            "PrimerApellido": ["García", "López"],
            "Oficina": ["CDMX", "GDL"],
            "Tour": ["Por el Centro Histórico", "Museando Ando"],
            "Mesa": ["Valuación", "Grúas"],
            "LLevaConyugue": ["NO", "SI"],
            "PrimerNombreConyugue": ["", "Pedro"],
            "PrimerApellidoConyugue": ["", "Martínez"],
            "QR": ["QR001", "QR002"],
            "QR_Conyugue": ["", "QR003"]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(self.excel_file, index=False)
        
        attendees = excel.read_attendees(self.excel_file)
        self.assertEqual(len(attendees), 2)
        
        for attendee in attendees:
            qr_buffer = qrs.generate_qr_local(attendee["QR"])
            self.assertIsInstance(qr_buffer, io.BytesIO)
            
            if attendee["LLevaConyugue"] and attendee["QR_Conyugue"]:
                qr_buffer_spouse = qrs.generate_qr_local(attendee["QR_Conyugue"])
                self.assertIsInstance(qr_buffer_spouse, io.BytesIO)


def run_tests():
    """Ejecuta todos los tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestExcelModule))
    suite.addTests(loader.loadTestsFromTestCase(TestQRsModule))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilsModule))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigModule))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    
    print("\n" + "=" * 70)
    if success:
        print(" TODOS LOS TESTS PASARON")
    else:
        print(" ALGUNOS TESTS FALLARN")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
