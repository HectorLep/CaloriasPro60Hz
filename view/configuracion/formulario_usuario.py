#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formulario para actualizar datos de usuario
"""

from .formularios import FormHandler
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from model.configuracion.servicios_usuario import UserService
from model.configuracion.mensajes import MessageHandler

class UpdateUserForm(FormHandler):
    def __init__(self, parent, user_service: UserService, restore_callback):
        self.parent = parent
        self.user_service = user_service
        self.restore_callback = restore_callback
        self.widgets = {}

    def create_form(self):
        edad, genero, peso, nivel_actividad, meta_cal, estatura = self.user_service.cargar_datos_usuario()

        # Frame de fondo principal
        self.widgets['bg_frame'] = QFrame(self.parent)
        self.widgets['bg_frame'].setGeometry(45, 100, 390, 385)
        self.widgets['bg_frame'].setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 35px;
            }
        """)

        # Estatura
        self.widgets['bg_frame_estatura'] = QFrame(self.parent)
        self.widgets['bg_frame_estatura'].setGeometry(65, 135, 125, 40)
        self.widgets['bg_frame_estatura'].setStyleSheet("""
            QFrame {
                background-color: #cccccc;
                border-radius: 20px;
            }
        """)

        self.widgets['label_estatura'] = QLabel("Estatura", self.parent)
        self.widgets['label_estatura'].setGeometry(82, 140, 100, 30)
        self.widgets['label_estatura'].setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        self.widgets['label_estatura'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.widgets['entry_estatura'] = QLineEdit(self.parent)
        self.widgets['entry_estatura'].setGeometry(200, 135, 210, 40)
        self.widgets['entry_estatura'].setText(f"{estatura} cm")
        self.widgets['entry_estatura'].setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: black;
                border: none;
                border-radius: 20px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.widgets['entry_estatura'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Objetivo calorías
        self.widgets['bg_frame_obj'] = QFrame(self.parent)
        self.widgets['bg_frame_obj'].setGeometry(65, 185, 125, 40)
        self.widgets['bg_frame_obj'].setStyleSheet("""
            QFrame {
                background-color: #cccccc;
                border-radius: 20px;
            }
        """)

        self.widgets['label_obj'] = QLabel("Objetivo kcal", self.parent)
        self.widgets['label_obj'].setGeometry(82, 190, 100, 30)
        self.widgets['label_obj'].setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        self.widgets['label_obj'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.widgets['entry_obj'] = QLineEdit(self.parent)
        self.widgets['entry_obj'].setGeometry(200, 185, 210, 40)
        self.widgets['entry_obj'].setText(str(meta_cal))
        self.widgets['entry_obj'].setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: black;
                border: none;
                border-radius: 20px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.widgets['entry_obj'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Nivel de actividad
        self.widgets['bg_frame_nvl'] = QFrame(self.parent)
        self.widgets['bg_frame_nvl'].setGeometry(65, 235, 125, 40)
        self.widgets['bg_frame_nvl'].setStyleSheet("""
            QFrame {
                background-color: #cccccc;
                border-radius: 20px;
            }
        """)

        self.widgets['label_nvl'] = QLabel("Nivel act", self.parent)
        self.widgets['label_nvl'].setGeometry(82, 240, 100, 30)
        self.widgets['label_nvl'].setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        self.widgets['label_nvl'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.widgets['combobox_nvl'] = QComboBox(self.parent)
        self.widgets['combobox_nvl'].setGeometry(200, 235, 210, 40)
        self.widgets['combobox_nvl'].addItems(["Sendatario", "Ligero", "Moderado", "Intenso"])
        self.widgets['combobox_nvl'].setCurrentText(nivel_actividad)
        self.widgets['combobox_nvl'].setStyleSheet("""
            QComboBox {
                background-color: #cccccc;
                color: black;
                border: none;
                border-radius: 20px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
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
        """)
        self.widgets['combobox_nvl'].setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Botón Actualizar
        self.widgets['boton_guardar'] = QPushButton("Actualizar datos", self.parent)
        self.widgets['boton_guardar'].setGeometry(120, 350, 250, 40)
        self.widgets['boton_guardar'].setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: black;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.widgets['boton_guardar'].setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.widgets['boton_guardar'].clicked.connect(self.save)

        # Botón Regresar
        self.widgets['boton_regresar'] = QPushButton("Regresar", self.parent)
        self.widgets['boton_regresar'].setGeometry(120, 410, 250, 40)
        self.widgets['boton_regresar'].setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: black;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.widgets['boton_regresar'].setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.widgets['boton_regresar'].clicked.connect(self.restore_callback)

        # Mostrar todos los widgets
        for widget in self.widgets.values():
            widget.show()

    def save(self):
        try:
            nueva_estatura = self.widgets['entry_estatura'].text().replace(" cm", "").strip()
            nueva_meta_calorias = self.widgets['entry_obj'].text().strip()
            nuevo_nivel_actividad = self.widgets['combobox_nvl'].currentText()

            edad, genero, peso, nivel_actividad, meta_cal, estatura = self.user_service.cargar_datos_usuario()

            if (nueva_estatura == str(estatura) and
                nueva_meta_calorias == str(meta_cal) and
                nuevo_nivel_actividad == nivel_actividad):
                MessageHandler.mostrar_info("Sin Cambios", "No se han realizado cambios.")
                return

            exito = self.user_service.actualizar_datos(nueva_estatura, nueva_meta_calorias, nuevo_nivel_actividad)

            if exito:
                MessageHandler.mostrar_info("Confirmación", "Datos actualizados correctamente.")
                self.restore_callback()
        except Exception as e:
            MessageHandler.mostrar_advertencia("Error", f"Hubo un problema: {e}")

    def hide_widgets(self):
        """Ocultar todos los widgets del formulario"""
        for widget in self.widgets.values():
            widget.hide()