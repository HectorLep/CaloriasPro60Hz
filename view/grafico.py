#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sección de gráficos y estadísticas
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush
import random

class SimpleChart(QWidget):
    """Widget para mostrar gráficos simples"""
    def __init__(self, chart_type="bar"):
        super().__init__()
        self.chart_type = chart_type
        self.data = []
        self.labels = []
        self.setMinimumHeight(300)
        
    def set_data(self, data, labels):
        self.data = data
        self.labels = labels
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configurar colores
        painter.fillRect(self.rect(), Qt.GlobalColor.darkGray)
        
        if not self.data:
            # Mostrar mensaje si no hay datos
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No hay datos para mostrar")
            return
            
        # Dibujar gráfico según el tipo
        if self.chart_type == "bar":
            self.draw_bar_chart(painter)
        elif self.chart_type == "line":
            self.draw_line_chart(painter)
        elif self.chart_type == "pie":
            self.draw_pie_chart(painter)
            
    def draw_bar_chart(self, painter):
        if not self.data:
            return
            
        margin = 50
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        max_value = max(self.data) if self.data else 1
        bar_width = width // len(self.data)
        
        colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, 
                 Qt.GlobalColor.yellow, Qt.GlobalColor.magenta, Qt.GlobalColor.cyan]
        
        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * height
            x = margin + i * bar_width
            y = self.height() - margin - bar_height
            
            painter.setBrush(QBrush(colors[i % len(colors)]))
            painter.drawRect(x + 5, y, bar_width - 10, bar_height)
            
            # Dibujar etiqueta
            painter.setPen(Qt.GlobalColor.white)
            if i < len(self.labels):
                painter.drawText(x, self.height() - 20, bar_width, 20, 
                               Qt.AlignmentFlag.AlignCenter, self.labels[i])
                
    def draw_line_chart(self, painter):
        if len(self.data) < 2:
            return
            
        margin = 50
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        max_value = max(self.data)
        min_value = min(self.data)
        value_range = max_value - min_value if max_value != min_value else 1
        
        points = []
        for i, value in enumerate(self.data):
            x = margin + (i / (len(self.data) - 1)) * width
            y = margin + height - ((value - min_value) / value_range) * height
            points.append((x, y))
            
        # Dibujar línea
        painter.setPen(QPen(Qt.GlobalColor.green, 3))
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
            
        # Dibujar puntos
        painter.setBrush(QBrush(Qt.GlobalColor.red))
        for x, y in points:
            painter.drawEllipse(x-3, y-3, 6, 6)

class Grafico(QWidget):
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
            QComboBox {
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
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Gráficos y Estadísticas")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        period_label = QLabel("Período:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Última semana", "Último mes", "Últimos 3 meses", "Último año"])
        
        chart_label = QLabel("Tipo de gráfico:")
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Barras", "Líneas", "Circular"])
        self.chart_combo.currentTextChanged.connect(self.change_chart_type)
        
        self.update_btn = QPushButton("Actualizar")
        self.update_btn.clicked.connect(self.update_chart)
        
        controls_layout.addWidget(period_label)
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(chart_label)
        controls_layout.addWidget(self.chart_combo)
        controls_layout.addWidget(self.update_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Gráfico principal
        chart_group = QGroupBox("Consumo de Calorías")
        chart_layout = QVBoxLayout(chart_group)
        
        self.main_chart = SimpleChart("bar")
        chart_layout.addWidget(self.main_chart)
        
        layout.addWidget(chart_group)
        
        # Estadísticas resumidas
        stats_group = QGroupBox("Estadísticas Resumidas")
        stats_layout = QHBoxLayout(stats_group)
        
        # Crear tarjetas de estadísticas
        self.create_stat_card(stats_layout, "Promedio Diario", "2,150 kcal", "#4CAF50")
        self.create_stat_card(stats_layout, "Máximo", "2,800 kcal", "#FF9800")
        self.create_stat_card(stats_layout, "Mínimo", "1,650 kcal", "#2196F3")
        self.create_stat_card(stats_layout, "Meta Diaria", "2,200 kcal", "#9C27B0")
        
        layout.addWidget(stats_group)
        
        # Cargar datos de ejemplo
        self.load_sample_data()
        
    def create_stat_card(self, layout, title, value, color):
        """Crear una tarjeta de estadística"""
        card = QFrame()
        card.setFixedSize(200, 100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        layout.addWidget(card)
        
    def change_chart_type(self, chart_type):
        """Cambiar el tipo de gráfico"""
        type_map = {
            "Barras": "bar",
            "Líneas": "line",
            "Circular": "pie"
        }
        
        if chart_type in type_map:
            self.main_chart.chart_type = type_map[chart_type]
            self.main_chart.update()
            
    def update_chart(self):
        """Actualizar el gráfico con nuevos datos"""
        # Aquí cargarías datos reales según el período seleccionado
        self.load_sample_data()
        
    def load_sample_data(self):
        """Cargar datos de ejemplo"""
        # Datos de ejemplo para los últimos 7 días
        sample_data = [2100, 2350, 1980, 2250, 2150, 2400, 2050]
        labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        self.main_chart.set_data(sample_data, labels)