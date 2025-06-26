#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contador de Calorías Pro 60Hz
Aplicación principal que inicializa la API y la GUI.
"""

import sys
import threading
import uvicorn
from PyQt6.QtWidgets import QApplication

# Se importa la instancia de la app FastAPI desde el archivo api.py
from controller.API.user.api import app as fastapi_app
from view.ventana_main.ventana_principal import MainWindow

def run_fastapi():
    """Función para ejecutar el servidor uvicorn en un hilo."""
    # El servidor se recarga automáticamente si hay cambios en el código.
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, reload=False)

def main():
    """
    Función principal que inicia la API en un hilo separado
    y luego lanza la aplicación de escritorio PyQt6.
    """
    # Iniciar la API de FastAPI en un hilo demonio
    # Un hilo demonio se cierra automáticamente cuando el programa principal termina.
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    
    # Inicializar la aplicación PyQt6
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar el bucle de eventos de la aplicación y salir cuando se cierre
    sys.exit(app.exec())

if __name__ == "__main__":
    main()