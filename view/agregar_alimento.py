#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sección para agregar nuevos alimentos a la base de datos
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QComboBox,
                             QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AgregarAlimento(QWidget):
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
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
                background-color: #555;
                border: 1px solid #777;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
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
        title = QLabel("Agregar Nuevo Alimento a la Base de Datos")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Formulario para nuevo alimento
        form_group = QGroupBox("Información Nutricional del Alimento")
        form_layout = QVBoxLayout(form_group)
        
        # Nombre del alimento
        name_layout = QHBoxLayout()
        name_label = QLabel("Nombre del alimento:")
        name_label.setMinimumWidth(180)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Pollo a la plancha, Arroz integral...")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Categoría
        category_layout = QHBoxLayout()
        category_label = QLabel("Categoría:")
        category_label.setMinimumWidth(180)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Carnes", "Pescados", "Lácteos", "Cereales", "Legumbres", 
            "Frutas", "Verduras", "Frutos secos", "Bebidas", "Dulces", "Otros"
        ])
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        form_layout.addLayout(category_layout)
        
        # Información nutricional por 100g
        nutrition_title = QLabel("Información Nutricional (por 100g):")
        nutrition_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        nutrition_title.setStyleSheet("margin-top: 15px; margin-bottom: 10px;")
        form_layout.addWidget(nutrition_title)
        
        # Calorías
        calories_layout = QHBoxLayout()
        calories_label = QLabel("Calorías:")
        calories_label.setMinimumWidth(180)
        self.calories_input = QDoubleSpinBox()
        self.calories_input.setMinimum(0)
        self.calories_input.setMaximum(9999.99)
        self.calories_input.setSuffix(" kcal")
        self.calories_input.setDecimals(2)
        calories_layout.addWidget(calories_label)
        calories_layout.addWidget(self.calories_input)
        calories_layout.addStretch()
        form_layout.addLayout(calories_layout)
        
        # Macronutrientes
        macros_layout = QHBoxLayout()
        
        # Proteínas
        protein_label = QLabel("Proteínas:")
        self.protein_input = QDoubleSpinBox()
        self.protein_input.setMinimum(0)
        self.protein_input.setMaximum(999.99)
        self.protein_input.setSuffix(" g")
        self.protein_input.setDecimals(2)
        
        # Carbohidratos
        carbs_label = QLabel("Carbohidratos:")
        self.carbs_input = QDoubleSpinBox()
        self.carbs_input.setMinimum(0)
        self.carbs_input.setMaximum(999.99)
        self.carbs_input.setSuffix(" g")
        self.carbs_input.setDecimals(2)
        
        # Grasas
        fats_label = QLabel("Grasas:")
        self.fats_input = QDoubleSpinBox()
        self.fats_input.setMinimum(0)
        self.fats_input.setMaximum(999.99)
        self.fats_input.setSuffix(" g")
        self.fats_input.setDecimals(2)
        
        macros_layout.addWidget(protein_label)
        macros_layout.addWidget(self.protein_input)
        macros_layout.addWidget(carbs_label)
        macros_layout.addWidget(self.carbs_input)
        macros_layout.addWidget(fats_label)
        macros_layout.addWidget(self.fats_input)
        form_layout.addLayout(macros_layout)
        
        # Fibra y azúcar
        fiber_sugar_layout = QHBoxLayout()
        
        fiber_label = QLabel("Fibra:")
        self.fiber_input = QDoubleSpinBox()
        self.fiber_input.setMinimum(0)
        self.fiber_input.setMaximum(999.99)
        self.fiber_input.setSuffix(" g")
        self.fiber_input.setDecimals(2)
        
        sugar_label = QLabel("Azúcares:")
        self.sugar_input = QDoubleSpinBox()
        self.sugar_input.setMinimum(0)
        self.sugar_input.setMaximum(999.99)
        self.sugar_input.setSuffix(" g")
        self.sugar_input.setDecimals(2)
        
        fiber_sugar_layout.addWidget(fiber_label)
        fiber_sugar_layout.addWidget(self.fiber_input)
        fiber_sugar_layout.addWidget(sugar_label)
        fiber_sugar_layout.addWidget(self.sugar_input)
        fiber_sugar_layout.addStretch()
        form_layout.addLayout(fiber_sugar_layout)
        
        # Notas
        notes_label = QLabel("Notas adicionales:")
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Información adicional sobre el alimento...")
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
        
        self.save_btn = QPushButton("Agregar a Base de Datos")
        self.save_btn.clicked.connect(self.save_food)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.save_btn)
        layout.addLayout(buttons_layout)
        
        # Tabla de alimentos en la base de datos
        database_group = QGroupBox("Alimentos en la Base de Datos")
        database_layout = QVBoxLayout(database_group)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar alimento...")
        self.search_input.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        database_layout.addLayout(search_layout)
        
        self.database_table = QTableWidget()
        self.database_table.setColumnCount(7)
        self.database_table.setHorizontalHeaderLabels([
            "Alimento", "Categoría", "Calorías", "Proteínas", "Carbohidratos", "Grasas", "Fibra"
        ])
        self.database_table.horizontalHeader().setStretchLastSection(True)
        self.database_table.setAlternatingRowColors(True)
        self.database_table.setStyleSheet("""
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
        
        database_layout.addWidget(self.database_table)
        layout.addWidget(database_group)
        
        # Cargar algunos datos de ejemplo
        self.load_sample_data()
        
    def clear_form(self):
        """Limpiar el formulario"""
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.calories_input.setValue(0)
        self.protein_input.setValue(0)
        self.carbs_input.setValue(0)
        self.fats_input.setValue(0)
        self.fiber_input.setValue(0)
        self.sugar_input.setValue(0)
        self.notes_input.clear()
        
    def save_food(self):
        """Guardar el alimento en la base de datos"""
        name = self.name_input.text()
        if not name:
            return
            
        category = self.category_combo.currentText()
        calories = f"{self.calories_input.value():.1f}"
        protein = f"{self.protein_input.value():.1f}g"
        carbs = f"{self.carbs_input.value():.1f}g"
        fats = f"{self.fats_input.value():.1f}g"
        fiber = f"{self.fiber_input.value():.1f}g"
        
        # Agregar a la tabla
        row_position = self.database_table.rowCount()
        self.database_table.insertRow(row_position)
        
        self.database_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.database_table.setItem(row_position, 1, QTableWidgetItem(category))
        self.database_table.setItem(row_position, 2, QTableWidgetItem(calories))
        self.database_table.setItem(row_position, 3, QTableWidgetItem(protein))
        self.database_table.setItem(row_position, 4, QTableWidgetItem(carbs))
        self.database_table.setItem(row_position, 5, QTableWidgetItem(fats))
        self.database_table.setItem(row_position, 6, QTableWidgetItem(fiber))
        
        # Limpiar formulario después de guardar
        self.clear_form()
        
    def filter_table(self):
        """Filtrar la tabla según el texto de búsqueda"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.database_table.rowCount()):
            item = self.database_table.item(row, 0)  # Columna del nombre
            if item is not None:
                should_show = search_text in item.text().lower()
                self.database_table.setRowHidden(row, not should_show)
    
    def load_sample_data(self):
        """Cargar algunos datos de ejemplo"""
        sample_foods = [
            ("Pollo a la plancha", "Carnes", "165", "25.0g", "0.0g", "3.6g", "0.0g"),
            ("Arroz blanco", "Cereales", "130", "2.7g", "28.2g", "0.3g", "0.4g"),
            ("Manzana", "Frutas", "52", "0.3g", "13.8g", "0.2g", "2.4g"),
            ("Brócoli", "Verduras", "34", "2.8g", "7.0g", "0.4g", "2.6g"),
            ("Salmón", "Pescados", "208", "25.4g", "0.0g", "12.4g", "0.0g")
        ]
        
        for food_data in sample_foods:
            row_position = self.database_table.rowCount()
            self.database_table.insertRow(row_position)
            
            for col, data in enumerate(food_data):
                self.database_table.setItem(row_position, col, QTableWidgetItem(data))