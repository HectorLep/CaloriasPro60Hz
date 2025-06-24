# Agregar_Alimento.py - Convertido a PyQt6 con principios SOLID y mejor espaciado
import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QComboBox,
                             QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from model.util.colores import *
from model.util.mensajes import *
from model.agregar_alimento.alimento_factory import SqliteAlimentoFactory


class CustomButton(QPushButton):
    """Botón personalizado con estilos similares a CTk"""
    def __init__(self, text, width=245, height=35, bg_color="#2ECC71", 
                 hover_color="#27AE60", text_color="black", corner_radius=20, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {corner_radius}px;
                font-size: 16px;
                font-weight: bold;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #7F8C8D;
                color: #BDC3C7;
            }}
        """)


class CustomEntry(QLineEdit):
    """Campo de entrada personalizado"""
    def __init__(self, placeholder="", width=245, height=35, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid #BDC3C7;
                border-radius: 17px;
                padding: 8px 15px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: black;
            }}
            QLineEdit:focus {{
                border-color: #3498DB;
                background-color: white;
            }}
        """)


class CustomComboBox(QComboBox):
    """ComboBox personalizado"""
    def __init__(self, width=245, height=35, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid #BDC3C7;
                border-radius: 17px;
                padding: 8px 15px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: black;
            }}
            QComboBox:focus {{
                border-color: #3498DB;
                background-color: white;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid #BDC3C7;
                background-color: white;
                selection-background-color: #3498DB;
            }}
        """)


class HeaderFrame(QFrame):
    """Frame para headers con estilo personalizado"""
    def __init__(self, width=245, height=35, bg_color="#34495E", parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 17px;
            }}
        """)


class HeaderLabel(QLabel):
    """Label para headers"""
    def __init__(self, text, color="white", font_size=16, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                font-weight: bold;
                background-color: transparent;
                font-family: Arial;
            }}
        """)


class InfoButton(QPushButton):
    """Botón de información personalizado"""
    def __init__(self, text="i", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 18px;
                font-style: italic;
                font-family: 'Times New Roman';
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)


class AgregarAlimentoView(QWidget):
    """Vista responsable únicamente de la interfaz gráfica (SRP)"""
    
    def __init__(self, parent_frame, color, on_agregar_callback, on_ayuda_callback):
        super().__init__(parent_frame)
        self.color = color
        self.on_agregar_callback = on_agregar_callback
        self.on_ayuda_callback = on_ayuda_callback
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Layout principal con más espaciado
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)  # Más margen general
        self.layout.setSpacing(30)  # Más espacio entre secciones principales
        
        # Header con botón de ayuda
        self._crear_header()
        
        # Contenido principal
        self._crear_contenido_principal()
        
        # Espaciador antes del botón API
        self.layout.addSpacing(40)  # Espacio extra antes del botón API
        
        # Botón API
        self._crear_boton_api()
        
        self.layout.addStretch()
    
    def _crear_header(self):
        """Crea el header con botón de ayuda"""
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.boton_ayuda = InfoButton("i")
        self.boton_ayuda.clicked.connect(self.on_ayuda_callback)
        header_layout.addWidget(self.boton_ayuda)
        
        self.layout.addLayout(header_layout)
    
    def _crear_contenido_principal(self):
        """Crea el contenido principal con las dos columnas"""
        content_layout = QHBoxLayout()
        content_layout.setSpacing(60)  # Más espacio entre columnas
        
        # Columna izquierda - Agregar alimento
        left_column = self._crear_columna_izquierda()
        content_layout.addWidget(left_column)
        
        # Columna derecha - Tipo de porción
        right_column = self._crear_columna_derecha()
        content_layout.addWidget(right_column)
        
        content_layout.addStretch()
        self.layout.addLayout(content_layout)
    
    def _crear_columna_izquierda(self):
        """Crea la columna izquierda para agregar alimento"""
        frame = QFrame()
        frame.setFixedWidth(300)  # Un poco más ancho
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)  # Más espacio entre elementos
        
        # Header
        header_frame = HeaderFrame(width=245, height=35, bg_color="#34495E")
        header_label = HeaderLabel("Agregar Alimentos")
        header_label.setParent(header_frame)
        header_label.move(10, 8)
        
        # Entry nombre
        self.entry_nombre = CustomEntry(
            placeholder="Ingrese el nombre del alimento",
            width=245, height=35
        )
        
        layout.addWidget(header_frame)
        layout.addWidget(self.entry_nombre)
        layout.addStretch()
        
        return frame
    
    def _crear_columna_derecha(self):
        """Crea la columna derecha para tipo de porción"""
        frame = QFrame()
        frame.setFixedWidth(300)  # Un poco más ancho
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)  # Más espacio entre elementos
        
        # Header
        header_frame = HeaderFrame(width=245, height=35, bg_color="#34495E")
        header_label = HeaderLabel("Porcion / 100gr")
        header_label.setParent(header_frame)
        header_label.move(10, 8)
        
        # ComboBox
        self.combo_box = CustomComboBox(width=245, height=35)
        self.combo_box.addItems(["Por porción", "100gr"])
        self.combo_box.currentTextChanged.connect(self.actualizar_interfaz)
        
        layout.addWidget(header_frame)
        layout.addWidget(self.combo_box)
        layout.addStretch()
        
        return frame
    
    def _crear_boton_api(self):
        """Crea el botón para buscar calorías con más separación"""
        api_layout = QHBoxLayout()
        api_layout.addStretch()
        
        self.api = CustomButton(
            "Buscar Calorías", 
            width=200, height=40,
            bg_color="#2ECC71", 
            hover_color="#27AE60",
            text_color="black"
        )
        self.api.clicked.connect(self._abrir_api_calorias)
        
        api_layout.addWidget(self.api)
        api_layout.addStretch()  # Centrar el botón
        self.layout.addLayout(api_layout)
    
    def actualizar_interfaz(self, seleccion):
        """Actualiza la interfaz cuando se selecciona un tipo de porción"""
        # Crear elementos de calorías si no existen
        if not hasattr(self, 'entry_calorias'):
            self._crear_elementos_calorias()
        
        # Actualizar texto del label según selección
        if seleccion == "100gr":
            self.label_cant_calorias.setText("Calorías por 100gr")
        elif seleccion == "Por porción":
            self.label_cant_calorias.setText("Calorías por porción")
        else:
            self.label_cant_calorias.setText("Calorías")
    
    def _crear_elementos_calorias(self):
        """Crea los elementos de entrada de calorías con mejor espaciado"""
        # Buscar el layout de contenido principal
        content_layout = self.layout.itemAt(1).layout()
        left_frame = content_layout.itemAt(0).widget()
        left_layout = left_frame.layout()
        
        # Agregar espacio antes de los elementos de calorías
        left_layout.insertSpacing(left_layout.count() - 1, 30)
        
        # Header para calorías
        calorias_header_frame = HeaderFrame(width=245, height=35, bg_color="#34495E")
        self.label_cant_calorias = HeaderLabel("Calorías")
        self.label_cant_calorias.setParent(calorias_header_frame)
        self.label_cant_calorias.move(10, 8)
        
        # Insertar header antes del stretch
        left_layout.insertWidget(left_layout.count() - 1, calorias_header_frame)
        
        # Agregar espacio entre header y entry
        left_layout.insertSpacing(left_layout.count() - 1, 15)
        
        # Entry calorías
        self.entry_calorias = CustomEntry(
            placeholder="Ingrese las calorías",
            width=245, height=35
        )
        
        # Insertar entry antes del stretch
        left_layout.insertWidget(left_layout.count() - 1, self.entry_calorias)
        
        # Botón agregar en la columna derecha con más espacio
        content_layout = self.layout.itemAt(1).layout()
        right_frame = content_layout.itemAt(1).widget()
        right_layout = right_frame.layout()
        
        # Agregar espacio antes del botón
        right_layout.insertSpacing(right_layout.count() - 1, 60)
        
        self.boton_agregar = CustomButton(
            "Añadir Alimento",
            width=240, height=50,
            bg_color="#2ECC71",
            hover_color="#27AE60",
            text_color="black"
        )
        self.boton_agregar.clicked.connect(self.on_agregar_callback)
        
        right_layout.insertWidget(right_layout.count() - 1, self.boton_agregar)
    
    def _abrir_api_calorias(self):
        """Abre la página web para buscar calorías"""
        webbrowser.open("https://fitia.app/es/calorias-informacion-nutricional/")
    
    def obtener_datos_formulario(self):
        """Obtiene los datos del formulario"""
        return {
            'nombre': self.entry_nombre.text().strip(),
            'calorias': getattr(self.entry_calorias, 'text', lambda: '')().strip(),
            'tipo_porcion': self.combo_box.currentText()
        }
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        self.entry_nombre.clear()
        if hasattr(self, 'entry_calorias'):
            self.entry_calorias.clear()


class Agregar_Alimento(QWidget):
    """
    Controlador principal que coordina la vista, servicios y repositorio.
    Convertido a PyQt6 siguiendo el principio de responsabilidad única (SRP).
    """
    
    def __init__(self, panel_principal, color, usuario=None):
        super().__init__(panel_principal)
        self.panel_principal = panel_principal
        self.color = color
        self.usuario = usuario if usuario else self._get_current_user()
        
        self._inicializar_dependencias()
        self._crear_vista()

    def _get_current_user(self):
        """Obtiene el usuario actual"""
        try:
            with open('usuario_actual.txt', 'r') as f:
                return f.read().strip()
        except:
            return "usuario_default"
    
    def _inicializar_dependencias(self):
        """Inicializa dependencias usando Factory Method puro"""
        self.factory = SqliteAlimentoFactory()
        self.alimento_service = self.factory.crear_alimento_service(self.usuario)
        self.notification_service = self.factory.crear_notification_service()
    
    def _crear_vista(self):
        """Crea la vista y establece los callbacks"""
        # Layout principal para todo el widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame principal con fondo
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: none;
            }
        """)
        main_layout.addWidget(main_frame)
        
        # Crear la vista dentro del frame
        self.vista = AgregarAlimentoView(
            parent_frame=main_frame,
            color=self.color,
            on_agregar_callback=self._manejar_agregar_alimento,
            on_ayuda_callback=self._mostrar_ayuda
        )
        
    def _mostrar_mensaje_bienvenida(self):
            """Muestra el mensaje de bienvenida desde el archivo central."""
            info = MENSAJES.get("agregar_alimento", {})
            titulo = info.get("titulo", "Agregar Alimento")
            mensaje = info.get("mensaje_html", "Bienvenido a agregar alimentos.")
            
            QTimer.singleShot(1000, lambda: self._mostrar_mensaje(mensaje, titulo))
                
    def _manejar_agregar_alimento(self):
        """Maneja la lógica de agregar un alimento (SRP - una sola responsabilidad)"""
        datos = self.vista.obtener_datos_formulario()
        
        # Verificar similares antes de procesar
        tiene_similares, similares = self.alimento_service.verificar_similares(datos['nombre'])
        if tiene_similares and similares:
            if not self._confirmar_agregar_con_similares(similares):
                return
        
        # Procesar la adición del alimento
        exito, mensaje = self.alimento_service.agregar_alimento(
            datos['nombre'], 
            datos['calorias'], 
            datos['tipo_porcion']
        )
        
        if exito:
            self._mostrar_exito("Operación exitosa", mensaje)
            self.vista.limpiar_formulario()
        else:
            self._mostrar_error("Error de validación", mensaje)
    
    def _confirmar_agregar_con_similares(self, similares: list) -> bool:
        """Confirma si el usuario quiere agregar el alimento a pesar de tener similares"""
        similares_texto = ", ".join(similares[:3])  # Mostrar solo los primeros 3
        mensaje = (f"Existen alimentos con nombres similares:\n{similares_texto}\n\n"
                  "¿Desea continuar agregando este nuevo alimento?")
        
        reply = QMessageBox.question(
            self,
            "Nombres similares encontrados",
            mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def _mostrar_ayuda(self):
        """Muestra la ayuda de la aplicación"""
        mensaje = ("Esta es la pestaña de agregar alimento, para agregar un alimento "
                  "debes insertar el nombre del alimento, las calorías por porción o por 100 gramos.")
        self._mostrar_mensaje(mensaje, "Agregar Alimento")
    
    def _mostrar_mensaje(self, mensaje, titulo):
        """Muestra un mensaje informativo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def _mostrar_error(self, titulo, mensaje):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
    
    def _mostrar_exito(self, titulo, mensaje):
        """Muestra un mensaje de éxito"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def __del__(self):
        """Limpia los recursos al destruir la instancia"""
        if hasattr(self, 'repository'):
            self.repository.cerrar_conexion()