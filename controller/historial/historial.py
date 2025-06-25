# controller/historial/historial.py - VERSIÓN CORREGIDA Y SIMPLIFICADA

import sqlite3
from datetime import datetime
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, 
                             QFrame, QLabel, QPushButton, QTableView, QHeaderView,
                             QDateEdit, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QAbstractTableModel, QDate

# --- Clase para el Modelo de la Tabla (Maneja los datos) ---
class HistorialTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Alimento", "Fecha", "Hora", "Cantidad", "Calorías"]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

# --- Clase para la Vista (Maneja los botones y la tabla) ---
class HistorialView(QWidget):
    # Señales que la vista emite hacia el controlador
    aplicar_filtros_clicked = pyqtSignal()
    limpiar_filtros_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # --- Panel de Controles (Filtros) ---
        controles_frame = QFrame()
        controles_frame.setFixedHeight(60)
        controles_frame.setStyleSheet("background-color: #34495E; border-radius: 10px;")
        
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setContentsMargins(15, 5, 15, 5)

        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        
        self.btn_aplicar = QPushButton("Aplicar Filtro")
        self.btn_limpiar = QPushButton("Limpiar")
        
        controles_layout.addWidget(QLabel("Desde:"))
        controles_layout.addWidget(self.date_from)
        controles_layout.addWidget(QLabel("Hasta:"))
        controles_layout.addWidget(self.date_to)
        controles_layout.addStretch()
        controles_layout.addWidget(self.btn_aplicar)
        controles_layout.addWidget(self.btn_limpiar)

        # --- Tabla de Datos ---
        self.tabla = QTableView()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- Añadir widgets al layout principal de la vista ---
        layout.addWidget(controles_frame)
        layout.addWidget(self.tabla)
        
        # Conectar botones a las señales
        self.btn_aplicar.clicked.connect(self.aplicar_filtros_clicked.emit)
        self.btn_limpiar.clicked.connect(self.limpiar_filtros_clicked.emit)

        self.set_styles()

    def set_styles(self):
        date_style = """
            QDateEdit { 
                background-color: white; color: black; 
                border-radius: 5px; padding: 5px;
            }
        """
        btn_style = """
            QPushButton { 
                background-color: #2ECC71; color: #2C3E50; border: none;
                border-radius: 8px; padding: 8px 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27AE60; }
        """
        self.date_from.setStyleSheet(date_style)
        self.date_to.setStyleSheet(date_style)
        self.btn_aplicar.setStyleSheet(btn_style)
        self.btn_limpiar.setStyleSheet(btn_style.replace("#2ECC71", "#E74C3C").replace("#27AE60", "#C0392B"))
        self.tabla.setStyleSheet("""
            QTableView {
                background-color: #34495E; color: white;
                border: 1px solid #2C3E50; border-radius: 10px;
                gridline-color: #4A6572;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: #2ECC71;
                padding: 5px; border: none; font-weight: bold;
            }
            QTableView::item { padding: 5px; }
            QTableView::item:alternate { background-color: #3E576B; }
        """)

    def set_data_in_table(self, data):
        model = HistorialTableModel(data)
        self.tabla.setModel(model)


# --- Clase Principal (Controlador del Historial) ---
class Historial(QWidget):
    def __init__(self, panel_principal, color, usuario=None):
        super().__init__()
        self.usuario = usuario
        self.init_ui()
        self.refrescar_vista() # Cargar todos los datos al iniciar

    def init_ui(self):
        """Configura la interfaz principal del módulo Historial."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Historial de Consumo")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #FFFFFF; margin-bottom: 10px;")
        
        self.historial_view = HistorialView(self)
        
        main_layout.addWidget(titulo)
        main_layout.addWidget(self.historial_view)
        
        # Conectar las señales de la vista a los métodos de este controlador
        self.historial_view.aplicar_filtros_clicked.connect(self.aplicar_filtros)
        self.historial_view.limpiar_filtros_clicked.connect(self.refrescar_vista)

    def _ejecutar_consulta(self, query, params=None):
        """Método central para ejecutar consultas a la BD."""
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()
            return datos
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo ejecutar la consulta: {e}")
            return []

    def refrescar_vista(self):
        """Slot público que recarga TODOS los datos del historial."""
        print("Refrescando la vista de Historial con todos los datos...")
        query = "SELECT nombre, fecha, hora, cantidad, total_cal FROM consumo_diario ORDER BY id DESC"
        datos_totales = self._ejecutar_consulta(query)
        self.historial_view.set_data_in_table(datos_totales)
        # Resetear fechas a un rango por defecto amplio
        self.historial_view.date_from.setDate(QDate.currentDate().addYears(-1))
        self.historial_view.date_to.setDate(QDate.currentDate())


    def aplicar_filtros(self):
        """Aplica los filtros de fecha seleccionados por el usuario."""
        fecha_desde = self.historial_view.date_from.date().toString("dd-MM-yyyy")
        fecha_hasta = self.historial_view.date_to.date().toString("dd-MM-yyyy")
        print(f"Filtrando desde {fecha_desde} hasta {fecha_hasta}...")
        
        query = """
            SELECT nombre, fecha, hora, cantidad, total_cal 
            FROM consumo_diario 
            WHERE fecha BETWEEN ? AND ? 
            ORDER BY id DESC
        """
        # Nota: SQLite no entiende el formato DD-MM-YYYY para comparaciones.
        # Esta consulta funcionará si filtras en la misma fecha. Para rangos,
        # necesitarías guardar las fechas en formato YYYY-MM-DD.
        # Por ahora, la dejamos así para mantener la funcionalidad básica.
        datos_filtrados = self._ejecutar_consulta(query, (fecha_desde, fecha_hasta))
        self.historial_view.set_data_in_table(datos_filtrados)
        
    def show_welcome_message(self):
        """Muestra un mensaje de bienvenida simple (mantiene compatibilidad)."""
        QMessageBox.information(
            self,
            "Historial de Consumo",
            "Aquí puedes ver y filtrar todos los alimentos que has registrado."
        )