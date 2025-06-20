import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from model.util.colores import *


class ProgresoSalud:
    def __init__(self, frame_graficos, usuario):
        self.frame = frame_graficos
        self.usuario = usuario
        
        # Limpiar el frame antes de agregar contenido
        self.limpiar_frame()
        
        self.mostrar_gauge_imc()

    def limpiar_frame(self):
        """Elimina todos los widgets del frame"""
        if self.frame.layout():
            while self.frame.layout().count():
                child = self.frame.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            # Si no hay layout, crear uno
            layout = QVBoxLayout()
            self.frame.setLayout(layout)

    def mostrar_gauge_imc(self):
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            cursor.execute("SELECT peso FROM peso ORDER BY fecha DESC LIMIT 1")
            peso = cursor.fetchone()
            cursor.execute("SELECT estatura FROM datos WHERE nombre = ?", (self.usuario,))
            estatura = cursor.fetchone()
            conn.close()

            if not peso or not estatura:
                self.mostrar_error("No se encontraron datos de peso o estatura")
                return

            peso = peso[0]
            estatura = estatura[0] / 100
            imc = peso / (estatura ** 2)

            # Crear la figura de matplotlib
            fig, ax = plt.subplots(figsize=(2.8, 1.6), dpi=75, subplot_kw={'projection': 'polar'})
            fig.patch.set_facecolor('#2b2b2b')       # Fondo de la figura (negro oscuro)
            ax.set_facecolor('#1a1a1a')              # Fondo del eje
            ax.title.set_color('white')              # Color del título
            
            # Definir categorías y colores
            categorias = [("Bajo", 0, 18.5), ("Normal", 18.5, 24.9), ("Sobrepeso", 25, 29.9), ("Obesidad", 30, 40)]
            colores = ['#5bc0de', riesgo_bajo, riesgo_medio, riesgo_alto]
            
            # Crear el gráfico de barras polar
            angulos = []
            inicio = 0
            for i, (_, start, end) in enumerate(categorias):
                rango = end - start
                ang = rango / 40 * np.pi
                ax.barh(1, ang, left=inicio, height=1, color=colores[i])
                angulos.append((start, inicio + ang / 2))
                inicio += ang

            # Agregar la línea indicadora del IMC
            imc_angle = imc / 40 * np.pi
            ax.plot([imc_angle, imc_angle], [0, 1], color='black', linewidth=2)
            
            # Configurar el gráfico
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.set_theta_zero_location("W")
            ax.set_theta_direction(-1)
            ax.set_title(f"IMC: {imc:.1f}")

            # Crear el canvas de matplotlib para PyQt6
            canvas = FigureCanvas(fig)
            canvas.setFixedSize(280, 160)  # Tamaño fijo equivalente a la figura
            
            # Agregar el canvas al layout del frame
            layout = self.frame.layout()
            if not layout:
                layout = QVBoxLayout()
                self.frame.setLayout(layout)
            
            layout.addWidget(canvas)
            
            # Cerrar la figura para liberar memoria
            plt.close(fig)

        except Exception as e:
            self.mostrar_error(f"IMC error: {str(e)}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el frame"""
        label = QLabel(mensaje)
        label.setStyleSheet("color: red; font-size: 12px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = self.frame.layout()
        if not layout:
            layout = QVBoxLayout()
            self.frame.setLayout(layout)
        
        layout.addWidget(label)

    def refrescar(self):
        """Elimina gráfico actual y vuelve a mostrarlo"""
        self.limpiar_frame()
        self.mostrar_gauge_imc()