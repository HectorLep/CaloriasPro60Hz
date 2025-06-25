from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont

class BarChartWidget(QWidget):
    """Widget especializado en dibujar un gráfico de barras con ejes."""
    def __init__(self):
        super().__init__()
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
        painter.fillRect(self.rect(), Qt.GlobalColor.darkGray)

        if not self.data:
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No hay datos para mostrar")
            return

        self.draw_bar_chart(painter)

    def draw_bar_chart(self, painter):
        margin_top, margin_bottom, margin_right, margin_left = 50, 50, 50, 80
        
        width = self.width() - margin_left - margin_right
        height = self.height() - margin_top - margin_bottom
        
        max_value = max(self.data) if self.data else 1
        bar_width = width // len(self.data) if len(self.data) > 0 else 0
        
        # --- DIBUJAR EJE Y ---
        painter.setPen(QPen(Qt.GlobalColor.white))
        num_labels = 5
        for i in range(num_labels + 1):
            value = max_value * (i / num_labels)
            y = self.height() - margin_bottom - (i * (height / num_labels))
            
            painter.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
            painter.drawLine(margin_left, int(y), self.width() - margin_right, int(y))
            
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(0, int(y - 10), margin_left - 10, 20, 
                           Qt.AlignmentFlag.AlignRight, f"{int(value)}")

        # --- DIBUJAR BARRAS Y EJE X ---
        colors = [Qt.GlobalColor.cyan, Qt.GlobalColor.green, Qt.GlobalColor.magenta, 
                  Qt.GlobalColor.yellow, Qt.GlobalColor.red, Qt.GlobalColor.blue]
        
        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * height if max_value > 0 else 0
            x = margin_left + i * bar_width
            y = self.height() - margin_bottom - bar_height
            
            painter.setBrush(QBrush(colors[i % len(colors)]))
            painter.setPen(Qt.PenStyle.NoPen) 
            painter.drawRect(int(x + 5), int(y), int(bar_width - 10), int(bar_height))
            
            painter.setPen(Qt.GlobalColor.white)
            if i < len(self.labels):
                painter.drawText(int(x), self.height() - margin_bottom + 5, int(bar_width), 20, 
                               Qt.AlignmentFlag.AlignCenter, self.labels[i])