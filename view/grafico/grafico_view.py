from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from .bar_chart_widget import BarChartWidget
from model.grafico.database_manager import ChartDataManager
from model.grafico.api_grafico import APICaloriesDataManager
from model.util.mensajes import MENSAJES

class GraficoView(QWidget):
    """
    La vista principal de la sección de gráficos. Construye la UI y delega la lógica.
    """
    def __init__(self, data_provider: ChartDataManager, usuario: str):
        super().__init__()
        self.data_provider = data_provider
        self.api_data_provider = APICaloriesDataManager()
        self.usuario = usuario
        self.data_fetchers = {
            "Consumo de Calorías": self.api_data_provider.get_calories_data,
            "Consumo de Agua": self.data_provider.get_water_data,
            "Registro de Peso": self.data_provider.get_weight_data
        }

        self.init_ui()
        self.update_chart()

    def mostrar_mensaje_bienvenida(self):
        """Muestra el mensaje de bienvenida para este módulo, cargándolo desde MENSAJES."""
        info = MENSAJES.get("grafico_view", {})
        titulo = info.get("titulo", "¡Bienvenido!")
        mensaje_html = info.get("mensaje_html", "Aquí puedes ver tu progreso.")

        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(mensaje_html)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet(
            "QMessageBox { background-color: #3c3c3c; border-radius: 15px; }"
            "QLabel { background-color: transparent; color: white; min-width: 450px; padding: 10px; }"
            "QMessageBox QPushButton { background-color: #2E86AB; color: white; border: none; padding: 10px 25px; border-radius: 8px; font-weight: bold; min-width: 80px; }"
            "QMessageBox QPushButton:hover { background-color: #1e5f7a; }"
        )
        msg.exec()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #3c3c3c; color: white; }
            QGroupBox { font-weight: bold; border: 1px solid #555; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QComboBox { background-color: #555; border: 1px solid #777; border-radius: 5px; padding: 8px; }
            QPushButton { background-color: #4CAF50; border: none; border-radius: 8px; padding: 10px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.boton_ayuda = QPushButton("?")
        self.boton_ayuda.setFixedSize(30, 30)
        self.boton_ayuda.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.boton_ayuda.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB; color: white; border: none; border-radius: 15px;
            }
            QPushButton:hover { background-color: #1e5f7a; }
            QPushButton:pressed { background-color: #0d3a4f; }
        """)
        self.boton_ayuda.clicked.connect(self.mostrar_ayuda_grafico)

        help_layout = QHBoxLayout()
        help_layout.addStretch()
        help_layout.addWidget(self.boton_ayuda)
        layout.addLayout(help_layout)

        title = QLabel("Gráficos")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(50)
        title.setStyleSheet("background-color: transparent; color: white; font-weight: bold; font-size: 24px; padding: 0px; margin: 0px; border: none;")
        layout.addWidget(title)

        controls_layout = QHBoxLayout()
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Última semana", "Último mes", "Últimos 3 meses", "Último año"])
        self.data_combo = QComboBox()
        self.data_combo.addItems(["Consumo de Calorías", "Consumo de Agua", "Registro de Peso"])
        self.update_btn = QPushButton("Actualizar")
        periodo_label = QLabel("Período:")
        periodo_label.setStyleSheet("background-color: transparent; color: white; font-weight: bold; font-size: 16px; padding: 0px; margin: 0px; border: none;")
        datos_label = QLabel("Datos:")
        datos_label.setStyleSheet("background-color: transparent; color: white; font-weight: bold; font-size: 16px; padding: 0px; margin: 0px; border: none;")
        controls_layout.addWidget(periodo_label)
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(datos_label)
        controls_layout.addWidget(self.data_combo)
        controls_layout.addWidget(self.update_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.update_btn.clicked.connect(self.update_chart)
        self.data_combo.currentTextChanged.connect(self.update_chart)
        self.period_combo.currentTextChanged.connect(self.update_chart)

        self.chart_group = QGroupBox("Estadísticas")
        chart_layout = QVBoxLayout(self.chart_group)
        self.main_chart = BarChartWidget()
        chart_layout.addWidget(self.main_chart)
        layout.addWidget(self.chart_group)

    def update_chart(self):
        periodo = self.period_combo.currentText()
        tipo_dato = self.data_combo.currentText()
        self.chart_group.setTitle(tipo_dato)
        fetch_function = self.data_fetchers.get(tipo_dato)
        if fetch_function:
            labels, data = fetch_function(period=periodo)
            color = QColor("#FF9800")
            if tipo_dato == "Consumo de Agua":
                color = QColor("#03A9F4")
            elif tipo_dato == "Registro de Peso":
                color = QColor("#9C27B0")
            self.main_chart.set_bar_color(color)
            self.main_chart.set_data(data, labels)

    def mostrar_ayuda_grafico(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ayuda - Gráficos")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(
            "📊 <b>Visualización de datos:</b><br><br>"
            "1. Selecciona el período y el tipo de datos que quieres analizar.<br>"
            "2. El gráfico se actualiza automáticamente al cambiar de opción.<br>"
            "3. Los colores representan distintos tipos de datos.<br><br>"
            "💡 <b>Tip:</b> El botón 'Actualizar' es útil si los datos cambian en segundo plano."
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""QMessageBox { 
                          background-color: #2b2b2b;
                          color: #ffffff;
                          } QLabel { 
                          background-color: transparent;
                          color: white;
                          font-size: 14px;
                          } QMessageBox QPushButton {
                              background-color: #4CAF50;
                              color: white;
                              border: none;
                              padding: 8px 16px;
                              border-radius: 5px;
                              font-weight: bold;
                              } QMessageBox QPushButton:hover {
                                  background-color: #45a049;
                                  }""")
        msg.exec()