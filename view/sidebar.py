#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Barra lateral de navegación
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon

class ProfileWidget(QWidget):
    """Widget para la foto de perfil"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Contenedor para la imagen de perfil
        self.profile_container = QFrame()
        self.profile_container.setFixedSize(80, 80)
        self.profile_container.setStyleSheet("""
            QFrame {
                background-color: #5a5a5a;
                border-radius: 40px;
                border: 2px solid #6a6a6a;
            }
        """)
        
        # Layout para la imagen
        profile_layout = QVBoxLayout(self.profile_container)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para la imagen de perfil
        self.profile_image = QLabel()
        self.profile_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_image.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 24px;
            }
        """)
        self.profile_image.setText("👤")  # Icono por defecto
        
        profile_layout.addWidget(self.profile_image)
        
        # Botón para agregar/cambiar foto
        self.add_photo_btn = QPushButton("+")
        self.add_photo_btn.setFixedSize(20, 20)
        self.add_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_photo_btn.clicked.connect(self.select_photo)
        
        # Posicionar el botón en la esquina
        self.add_photo_btn.setParent(self.profile_container)
        self.add_photo_btn.move(60, 60)
        
        # Nombre de usuario
        self.username_label = QLabel("Test2")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
            }
        """)
        
        layout.addWidget(self.profile_container)
        layout.addWidget(self.username_label)
        
    def select_photo(self):
        """Seleccionar foto de perfil"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar foto de perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Redimensionar y hacer circular la imagen
                scaled_pixmap = pixmap.scaled(76, 76, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                self.profile_image.setPixmap(scaled_pixmap)
                self.profile_image.setText("")

class NavigationButton(QPushButton):
    """Botón de navegación personalizado"""
    def __init__(self, text, icon_text=""):
        super().__init__()
        self.setText(f"{icon_text}  {text}")
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background-color: #5a5a5a;
            }
        """)

class Sidebar(QWidget):
    """Barra lateral principal"""
    section_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(0)
        
        # Widget de perfil
        self.profile_widget = ProfileWidget()
        layout.addWidget(self.profile_widget)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #4a4a4a; }")
        layout.addWidget(separator)
        layout.addSpacing(20)
        
        # Botones de navegación
        self.create_navigation_buttons(layout)
        
        # Espaciador para empujar todo hacia arriba
        layout.addStretch()
        
    def create_navigation_buttons(self, layout):
        """Crear botones de navegación"""
        buttons_data = [
            ("Registrar Alimento", "📝", "registrar"),
            ("Agregar Alimento", "➕", "agregar"),
            ("Gráfico", "📊", "grafico"),
            ("Historial", "🕐", "historial"),
            ("Settings", "⚙️", "settings"),
            ("Salud", "🛡️", "salud"),
            ("Menu", "📋", "menu")
        ]
        
        for text, icon, section_id in buttons_data:
            btn = NavigationButton(text, icon)
            btn.clicked.connect(lambda checked, s=section_id: self.section_changed.emit(s))
            layout.addWidget(btn)
            layout.addSpacing(5)