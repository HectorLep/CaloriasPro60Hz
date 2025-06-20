#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historial de consumo de alimentos
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QComboBox, QLineEdit, QGroupBox,
                             QHeaderView, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class Historial(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []  # Lista para almacenar los datos del historial
        self.filtered_data = []  # Datos filtrados
        self.init_ui()
        self.load_sample_data()  # Cargar datos de ejemplo
        
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
            QLineEdit, QComboBox, QDateEdit {
                background-color: #555;
                border: 1px solid #777;
                border-radius: 5px;
                padding: 8px;
                color: white;
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
            QTableWidget {
                background-color: #555;
                alternate-background-color: #606060;
                gridline-color: #777;
                selection-background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #666;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #777;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Historial de Consumo")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filtros
        filters_group = QGroupBox("Filtros de Búsqueda")
        filters_layout = QVBoxLayout(filters_group)
        
        # Primera fila de filtros
        filters_row1 = QHBoxLayout()
        
        # Rango de fechas
        date_label = QLabel("Desde:")
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        
        date_to_label = QLabel("Hasta:")
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        filters_row1.addWidget(date_label)
        filters_row1.addWidget(self.date_from)
        filters_row1.addWidget(date_to_label)
        filters_row1.addWidget(self.date_to)
        filters_row1.addStretch()
        
        # Segunda fila de filtros
        filters_row2 = QHBoxLayout()
        
        # Buscar por nombre
        search_label = QLabel("Buscar alimento:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre del alimento...")
        self.search_input.textChanged.connect(self.filter_table)
        
        # Filtrar por momento del día
        meal_label = QLabel("Momento del día:")
        self.meal_filter = QComboBox()
        self.meal_filter.addItems(["Todos", "Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena", "Otro"])
        self.meal_filter.currentTextChanged.connect(self.filter_table)
        
        filters_row2.addWidget(search_label)
        filters_row2.addWidget(self.search_input)
        filters_row2.addWidget(meal_label)
        filters_row2.addWidget(self.meal_filter)
        
        # Botones de filtro
        filters_row3 = QHBoxLayout()
        
        self.filter_btn = QPushButton("Aplicar Filtros de Fecha")
        self.filter_btn.clicked.connect(self.apply_date_filter)
        
        self.clear_btn = QPushButton("Limpiar Filtros")
        self.clear_btn.clicked.connect(self.clear_filters)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.export_btn = QPushButton("Exportar CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        filters_row3.addWidget(self.filter_btn)
        filters_row3.addWidget(self.clear_btn)
        filters_row3.addWidget(self.export_btn)
        filters_row3.addStretch()
        
        filters_layout.addLayout(filters_row1)
        filters_layout.addLayout(filters_row2)
        filters_layout.addLayout(filters_row3)
        
        layout.addWidget(filters_group)
        
        # Estadísticas rápidas
        stats_group = QGroupBox("Estadísticas del Período")
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_calories_label = QLabel("Calorías Totales: 0")
        self.total_foods_label = QLabel("Alimentos Registrados: 0")
        self.avg_calories_label = QLabel("Promedio Diario: 0")
        
        stats_layout.addWidget(self.total_calories_label)
        stats_layout.addWidget(self.total_foods_label)
        stats_layout.addWidget(self.avg_calories_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_group)
        
        # Tabla de historial
        self.create_table()
        layout.addWidget(self.table)
        
    def create_table(self):
        """Crear la tabla de historial"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        headers = ["Fecha", "Hora", "Alimento", "Cantidad", "Calorías", "Momento del Día"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configurar la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Configurar el ancho de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Hora
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Alimento
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Calorías
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Momento del día
        
    def load_sample_data(self):
        """Cargar datos de ejemplo"""
        from datetime import datetime, timedelta
        import random
        
        foods = [
            ("Pan tostado", 80), ("Café con leche", 60), ("Huevos revueltos", 155),
            ("Pollo a la plancha", 165), ("Arroz blanco", 130), ("Ensalada mixta", 45),
            ("Manzana", 52), ("Yogur natural", 59), ("Pasta", 131), ("Salmón", 208)
        ]
        
        meals = ["Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena"]
        
        # Generar datos para los últimos 15 días
        for i in range(45):
            date = datetime.now() - timedelta(days=random.randint(0, 15))
            food_name, base_calories = random.choice(foods)
            quantity = random.randint(50, 200)
            calories = int((base_calories * quantity) / 100)
            meal = random.choice(meals)
            
            self.data.append({
                "fecha": date.strftime("%d/%m/%Y"),
                "hora": date.strftime("%H:%M"),
                "alimento": food_name,
                "cantidad": f"{quantity}g",
                "calorias": calories,
                "momento": meal,
                "datetime": date
            })
        
        # Ordenar por fecha (más reciente primero)
        self.data.sort(key=lambda x: x["datetime"], reverse=True)
        self.filtered_data = self.data.copy()
        self.update_table()
        self.update_statistics()
    
    def update_table(self):
        """Actualizar la tabla con los datos filtrados"""
        self.table.setRowCount(len(self.filtered_data))
        
        for row, item in enumerate(self.filtered_data):
            self.table.setItem(row, 0, QTableWidgetItem(item["fecha"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["hora"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["alimento"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["cantidad"]))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["calorias"])))
            self.table.setItem(row, 5, QTableWidgetItem(item["momento"]))
    
    def update_statistics(self):
        """Actualizar las estadísticas"""
        if not self.filtered_data:
            self.total_calories_label.setText("Calorías Totales: 0")
            self.total_foods_label.setText("Alimentos Registrados: 0")
            self.avg_calories_label.setText("Promedio Diario: 0")
            return
        
        total_calories = sum(item["calorias"] for item in self.filtered_data)
        total_foods = len(self.filtered_data)
        
        # Calcular días únicos para el promedio
        unique_dates = set(item["fecha"] for item in self.filtered_data)
        days_count = len(unique_dates) if unique_dates else 1
        avg_calories = total_calories / days_count
        
        self.total_calories_label.setText(f"Calorías Totales: {total_calories:,}")
        self.total_foods_label.setText(f"Alimentos Registrados: {total_foods}")
        self.avg_calories_label.setText(f"Promedio Diario: {avg_calories:.0f}")
    
    def filter_table(self):
        """Filtrar la tabla por texto de búsqueda y momento del día"""
        search_text = self.search_input.text().lower()
        meal_filter = self.meal_filter.currentText()
        
        self.filtered_data = []
        
        for item in self.data:
            # Filtro por texto de búsqueda
            if search_text and search_text not in item["alimento"].lower():
                continue
            
            # Filtro por momento del día
            if meal_filter != "Todos" and item["momento"] != meal_filter:
                continue
            
            self.filtered_data.append(item)
        
        self.update_table()
        self.update_statistics()
    
    def apply_date_filter(self):
        """Aplicar filtros de fecha"""
        from_date = self.date_from.date().toPython()
        to_date = self.date_to.date().toPython()
        
        # Filtrar por rango de fechas
        temp_data = []
        for item in self.data:
            item_date = item["datetime"].date()
            if from_date <= item_date <= to_date:
                temp_data.append(item)
        
        self.data = temp_data
        self.filter_table()  # Aplicar también los otros filtros
    
    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.search_input.clear()
        self.meal_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        
        # Recargar datos de ejemplo
        self.data = []
        self.load_sample_data()
    
    def export_to_csv(self):
        """Exportar los datos filtrados a CSV"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        import csv
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", "historial_consumo.csv", "CSV files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Escribir encabezados
                    writer.writerow(["Fecha", "Hora", "Alimento", "Cantidad", "Calorías", "Momento del Día"])
                    
                    # Escribir datos
                    for item in self.filtered_data:
                        writer.writerow([
                            item["fecha"], item["hora"], item["alimento"],
                            item["cantidad"], item["calorias"], item["momento"]
                        ])
                
                QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
    
    def add_consumption_record(self, food_name, quantity, calories, meal_time):
        """Método para agregar un nuevo registro desde otras secciones"""
        from datetime import datetime
        
        now = datetime.now()
        new_record = {
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M"),
            "alimento": food_name,
            "cantidad": f"{quantity}g",
            "calorias": calories,
            "momento": meal_time,
            "datetime": now
        }
        
        self.data.insert(0, new_record)  # Insertar al principio (más reciente)
        self.filter_table()  # Actualizar la vista