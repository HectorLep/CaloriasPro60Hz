#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formulario para configurar recordatorios
"""

from .formularios import FormHandler
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                             QCheckBox, QPushButton, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from model.configuracion.servicios_usuario import UserService
from model.configuracion.mensajes import MessageHandler

class ReminderForm(FormHandler):
    def __init__(self, parent, user_service: UserService):
        self.parent = parent
        self.user_service = user_service
        self.widgets = {}
        self.ventana_recordatorio = None

    def create_form(self):
        self.ventana_recordatorio = QDialog(self.parent)
        self.ventana_recordatorio.setWindowTitle("Configurar Recordatorio de Peso")
        self.ventana_recordatorio.setFixedSize(400, 230)
        self.ventana_recordatorio.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Estilo del diálogo
        self.ventana_recordatorio.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QLabel {
                background-color: #1e3a5f;
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #cccccc;
                color: black;
                border: none;
                border-radius: 10px;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }
            QCheckBox {
                color: white;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: #1e3a5f;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout = QVBoxLayout(self.ventana_recordatorio)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Etiqueta de frecuencia
        self.widgets['label_recordatorio'] = QLabel("Frecuencia de Recordatorio")
        self.widgets['label_recordatorio'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets['label_recordatorio'].setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.widgets['label_recordatorio'].setFixedHeight(40)
        layout.addWidget(self.widgets['label_recordatorio'])
        
        # ComboBox de tiempo
        self.widgets['tiempo_recordatorio_combobox'] = QComboBox()
        self.widgets['tiempo_recordatorio_combobox'].addItems([
            "1 día", "3 días", "5 días", "1 semana", "1 mes"
        ])
        self.widgets['tiempo_recordatorio_combobox'].setFixedHeight(35)
        layout.addWidget(self.widgets['tiempo_recordatorio_combobox'])
        
        # CheckBox para activar recordatorio
        self.widgets['activar_recordatorio_checkbox'] = QCheckBox("Activar Recordatorio")
        self.widgets['activar_recordatorio_checkbox'].setChecked(True)
        layout.addWidget(self.widgets['activar_recordatorio_checkbox'])
        
        # Botón guardar
        self.widgets['guardar_button'] = QPushButton("Guardar Configuración")
        self.widgets['guardar_button'].setFixedHeight(40)
        self.widgets['guardar_button'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['guardar_button'].clicked.connect(self.save)
        layout.addWidget(self.widgets['guardar_button'])
        
        self.load_initial_values()
        self.ventana_recordatorio.exec()

    def load_initial_values(self):
        estado, frecuencia = self.user_service.cargar_configuracion_recordatorio()
        self.widgets['activar_recordatorio_checkbox'].setChecked(estado == "on")
        
        # Buscar el índice de la frecuencia en el combobox
        index = self.widgets['tiempo_recordatorio_combobox'].findText(frecuencia)
        if index >= 0:
            self.widgets['tiempo_recordatorio_combobox'].setCurrentIndex(index)

    def save(self):
        estado = "on" if self.widgets['activar_recordatorio_checkbox'].isChecked() else "off"
        frecuencia = self.widgets['tiempo_recordatorio_combobox'].currentText()

        exito = self.user_service.guardar_configuracion_recordatorio(estado, frecuencia)

        if exito:
            MessageHandler.mostrar_info("Confirmación", "Configuración guardada correctamente.")
            self.ventana_recordatorio.accept()