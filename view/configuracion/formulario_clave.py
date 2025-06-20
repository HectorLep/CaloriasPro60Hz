#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formulario para actualizar contraseña
"""

from .formularios import FormHandler
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from model.configuracion.servicios_usuario import UserService
from model.configuracion.mensajes import MessageHandler

class PasswordForm(FormHandler):
    def __init__(self, parent, user_service: UserService):
        self.parent = parent
        self.user_service = user_service
        self.widgets = {}
        self.nueva_ventana = None

    def create_form(self):
        self.nueva_ventana = QDialog(self.parent)
        self.nueva_ventana.setWindowTitle("Actualizar Contraseña")
        self.nueva_ventana.setFixedSize(400, 400)
        self.nueva_ventana.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Estilo del diálogo
        self.nueva_ventana.setStyleSheet("""
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
            QLineEdit {
                background-color: #f0f0f0;
                color: black;
                border: none;
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
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
        
        layout = QVBoxLayout(self.nueva_ventana)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Nombre de usuario
        self.widgets['nombre_label'] = QLabel(f"Nombre de Usuario: {self.user_service.usuario}")
        self.widgets['nombre_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets['nombre_label'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['nombre_label'].setFixedHeight(40)
        layout.addWidget(self.widgets['nombre_label'])
        
        # Contraseña anterior
        self.widgets['contra_anterior_label'] = QLabel("Contraseña Anterior")
        self.widgets['contra_anterior_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets['contra_anterior_label'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['contra_anterior_label'].setFixedHeight(40)
        layout.addWidget(self.widgets['contra_anterior_label'])
        
        self.widgets['contra_anterior_entry'] = QLineEdit()
        self.widgets['contra_anterior_entry'].setPlaceholderText("Introduce tu contraseña anterior")
        self.widgets['contra_anterior_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_anterior_entry'].setFixedHeight(35)
        layout.addWidget(self.widgets['contra_anterior_entry'])
        
        # Nueva contraseña
        self.widgets['nueva_contra_label'] = QLabel("Nueva Contraseña")
        self.widgets['nueva_contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets['nueva_contra_label'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['nueva_contra_label'].setFixedHeight(40)
        layout.addWidget(self.widgets['nueva_contra_label'])
        
        self.widgets['nueva_contra_entry'] = QLineEdit()
        self.widgets['nueva_contra_entry'].setPlaceholderText("Introduce la nueva contraseña")
        self.widgets['nueva_contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['nueva_contra_entry'].setFixedHeight(35)
        layout.addWidget(self.widgets['nueva_contra_entry'])
        
        # Confirmar contraseña
        self.widgets['confirmar_contra_label'] = QLabel("Confirmar Nueva Contraseña")
        self.widgets['confirmar_contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets['confirmar_contra_label'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['confirmar_contra_label'].setFixedHeight(40)
        layout.addWidget(self.widgets['confirmar_contra_label'])
        
        self.widgets['confirmar_contra_entry'] = QLineEdit()
        self.widgets['confirmar_contra_entry'].setPlaceholderText("Confirma la nueva contraseña")
        self.widgets['confirmar_contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['confirmar_contra_entry'].setFixedHeight(35)
        layout.addWidget(self.widgets['confirmar_contra_entry'])
        
        # Botón actualizar
        self.widgets['actualizar_contra_button'] = QPushButton("Actualizar Contraseña")
        self.widgets['actualizar_contra_button'].setFixedHeight(40)
        self.widgets['actualizar_contra_button'].setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.widgets['actualizar_contra_button'].clicked.connect(self.save)
        layout.addWidget(self.widgets['actualizar_contra_button'])
        
        self.nueva_ventana.exec()

    def save(self):
        contra_anterior = self.widgets['contra_anterior_entry'].text()
        nueva_contra = self.widgets['nueva_contra_entry'].text()
        confirmar_contra = self.widgets['confirmar_contra_entry'].text()

        if not contra_anterior or not nueva_contra or not confirmar_contra:
            MessageHandler.mostrar_advertencia("Advertencia", "Completa todos los campos.")
            return

        if nueva_contra != confirmar_contra:
            MessageHandler.mostrar_advertencia("Advertencia", "Las contraseñas no coinciden.")
            return

        if self.user_service.actualizar_contrasena(contra_anterior, nueva_contra):
            MessageHandler.mostrar_info("Confirmación", "Contraseña actualizada correctamente.")
            self.nueva_ventana.accept()
        else:
            MessageHandler.mostrar_advertencia("Error", "Contraseña anterior incorrecta.")