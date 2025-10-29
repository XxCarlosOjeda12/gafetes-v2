#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Automático de Gafetes para Reunión Anual de Directores 2025

Punto de entrada principal que delega la ejecución al módulo CLI.
Este archivo se mantiene mínimo para separar la lógica de negocio.

Versión: 2.0.0 (Refactorizado y modularizado)
Compatible con Python 3.13.7
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main

if __name__ == "__main__":
    main()
