#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contador de Calorías Pro 60Hz
Aplicación principal
"""

import sys
from PyQt6.QtWidgets import QApplication
from view.ventana_main.ventana_principal import MainWindow

def main():
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
                
    sys.exit(app.exec())

if __name__ == "__main__":
    main()