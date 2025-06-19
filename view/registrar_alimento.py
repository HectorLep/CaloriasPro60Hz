#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sección para registrar alimentos consumidos
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QComboBox,
                             QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RegistrarAlimento(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QSpinBox, QComboBox, QTextEdit {
                background-color: #555;
                border: 1px solid #777;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título de la sección
        title = QLabel("Registrar Alimento Consumido")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Formulario de registro
        form_group = QGroupBox("Información del Alimento")
        form_layout = QVBoxLayout(form_group)
        
        # Nombre del alimento
        name_layout = QHBoxLayout()
        name_label = QLabel("Nombre del alimento:")
        name_label.setMinimumWidth(150)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Manzana, Pollo a la plancha...")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Cantidad y unidad
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("Cantidad:")
        quantity_label.setMinimumWidth(150)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999)
        self.quantity_input.setSuffix(" g")
        
        unit_label = QLabel("Unidad:")
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["gramos", "ml", "unidades", "porciones", "cucharadas", "tazas"])
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)
        quantity_layout.addWidget(unit_label)
        quantity_layout.addWidget(self.unit_combo)
        form_layout.addLayout(quantity_layout)
        
        # Calorías
        calories_layout = QHBoxLayout()
        calories_label = QLabel("Calorías (por 100g):")
        calories_label.setMinimumWidth(150)
        self.calories_input = QSpinBox()
        self.calories_input.setMinimum(0)
        self.calories_input.setMaximum(9999)
        self.calories_input.setSuffix(" kcal")
        calories_layout.addWidget(calories_label)
        calories_layout.addWidget(self.calories_input)
        calories_layout.addStretch()
        form_layout.addLayout(calories_layout)
        
        # Momento del día
        meal_layout = QHBoxLayout()
        meal_label = QLabel("Momento del día:")
        meal_label.setMinimumWidth(150)
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(["Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena", "Otro"])
        meal_layout.addWidget(meal_label)
        meal_layout.addWidget(self.meal_combo)
        meal_layout.addStretch()
        form_layout.addLayout(meal_layout)
        
        # Notas
        notes_label = QLabel("Notas adicionales:")
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Notas opcionales sobre el alimento...")
        form_layout.addWidget(notes_label)
        form_layout.addWidget(self.notes_input)
        
        layout.addWidget(form_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.save_btn = QPushButton("Registrar Alimento")
        self.save_btn.clicked.connect(self.save_food)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.save_btn)
        layout.addLayout(buttons_layout)
        
        # Tabla de alimentos recientes
        recent_group = QGroupBox("Alimentos Registrados Hoy")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["Alimento", "Cantidad", "Calorías", "Momento", "Hora"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: #555;
                alternate-background-color: #606060;
                gridline-color: #777;
            }
            QHeaderView::section {
                background-color: #666;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        recent_layout.addWidget(self.recent_table)
        layout.addWidget(recent_group)
        
    def clear_form(self):
        """Limpiar el formulario"""
        self.name_input.clear()
        self.quantity_input.setValue(1)
        self.unit_combo.setCurrentIndex(0)
        self.calories_input.setValue(0)
        self.meal_combo.setCurrentIndex(0)
        self.notes_input.clear()
        
    def save_food(self):
        """Guardar el alimento registrado"""
        # Aquí implementarías la lógica para guardar el alimento
        # Por ahora solo mostraremos un mensaje o agregaremos a la tabla
        
        name = self.name_input.text()
        if not name:
            return
            
        quantity = f"{self.quantity_input.value()} {self.unit_combo.currentText()}"
        calories = f"{self.calories_input.value()} kcal"
        meal = self.meal_combo.currentText()
        
        # Agregar a la tabla
        row_position = self.recent_table.rowCount()
        self.recent_table.insertRow(row_position)
        
        self.recent_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.recent_table.setItem(row_position, 1, QTableWidgetItem(quantity))
        self.recent_table.setItem(row_position, 2, QTableWidgetItem(calories))
        self.recent_table.setItem(row_position, 3, QTableWidgetItem(meal))
        self.recent_table.setItem(row_position, 4, QTableWidgetItem("Ahora"))
        
        # Limpiar formulario después de guardar
        self.clear_form()