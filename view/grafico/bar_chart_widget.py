from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QLinearGradient

class BarChartWidget(QWidget):
    """Widget especializado en dibujar un gráfico de barras con ejes y diseño mejorado."""
    def __init__(self):
        super().__init__()
        self.data = []
        self.labels = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.bar_color = QColor("#00bcd4") 

    def set_data(self, data, labels):
        self.data = data
        self.labels = labels
        self.update()

    def set_bar_color(self, color: QColor):
        """Establece el color de las barras del gráfico."""
        self.bar_color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#3c3c3c")) # Fondo consistente

        if not self.data:
            painter.setPen(QColor("#ffffff"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No hay datos para mostrar")
            return

        self.draw_bar_chart(painter)

    def draw_bar_chart(self, painter):
        margin_top, margin_bottom, margin_right, margin_left = 50, 50, 50, 80
        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom
        max_value = max(self.data) if self.data else 1
        num_bars = len(self.data) if len(self.data) > 0 else 1
        bar_width = min(60, chart_width // num_bars)
        total_bars_width = num_bars * bar_width
        x_offset = (chart_width - total_bars_width) / 2
        
        axis_pen = QPen(QColor("#777777"), 1.5)
        painter.setPen(axis_pen)
        painter.drawLine(margin_left, margin_top, margin_left, self.height() - margin_bottom) # Eje Y
        painter.drawLine(margin_left, self.height() - margin_bottom, self.width() - margin_right, self.height() - margin_bottom) # Eje X
        
        label_font = QFont("Arial", 9)
        painter.setFont(label_font)
        
        num_labels_y = 5
        for i in range(num_labels_y + 1):
            value = max_value * (i / num_labels_y)
            y = self.height() - margin_bottom - (i * (chart_height / num_labels_y))
            
            painter.setPen(QPen(QColor("#cccccc")))
            painter.drawText(0, int(y - 10), margin_left - 10, 20,
                           Qt.AlignmentFlag.AlignRight, f"{int(value)}")

        
        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            x = margin_left + x_offset + i * bar_width
            y = self.height() - margin_bottom - bar_height
            
            # ""Relleno" de la barra
            gradient = QLinearGradient(x, y, x, y + bar_height)
            gradient.setColorAt(0, self.bar_color.lighter(130))
            gradient.setColorAt(1, self.bar_color)
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x + 5), int(y), int(bar_width - 10), int(bar_height), 5, 5)
            
            # "Relieve"
            border_pen = QPen(self.bar_color.lighter(170), 1.5) 
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush) 
            painter.drawRoundedRect(int(x + 5), int(y), int(bar_width - 10), int(bar_height), 5, 5)
            painter.setPen(QColor("#cccccc"))
            if i < len(self.labels):
                painter.drawText(int(x), self.height() - margin_bottom + 5, int(bar_width), 20,
                               Qt.AlignmentFlag.AlignCenter, self.labels[i])
    
        painter.setPen(QPen(QColor("#555555"), 1, Qt.PenStyle.DashLine))
        for i in range(num_labels_y + 1):
            if i > 0:
                y = self.height() - margin_bottom - (i * (chart_height / num_labels_y))
                painter.drawLine(margin_left, int(y), self.width() - margin_right, int(y))