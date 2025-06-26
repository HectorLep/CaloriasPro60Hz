# iniciar_sesion_form.py (Versión refactorizada)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFrame, QMessageBox)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from model.login.auth_service import IAuthService
from model.util.colores import *
from .form import *

class IniciarSesionForm(IForm, QWidget):

    volver_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: IAuthService, on_success, on_back):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_back = on_back
        self.widgets = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border: 2px solid {azul_medio_oscuro};
                border-radius: 20px;
                padding: 15px;
                max-width: 240px;
            }}
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(6)

        titulo = QLabel("Iniciar Sesión")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro}; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)

        # << CAMBIO 1: Label de Usuario (sin cambios, pero ahora apunta a un Entry) >>
        self.widgets['users_label'] = QLabel("Usuario")
        self.widgets['users_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial; border-radius: 15px; padding: 5px;
                min-width: 120px; min-height: 25px;
            }}
        """)
        self.widgets['users_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['users_label'])

        # << CAMBIO 2: QComboBox reemplazado por QLineEdit >>
        self.widgets['usuario_entry'] = QLineEdit()
        self.widgets['usuario_entry'].setPlaceholderText("Escribe tu usuario")
        self.widgets['usuario_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry}; color: black; border-radius: 15px;
                padding: 6px 10px; min-width: 120px; min-height: 28px; font: 14px Arial;
            }}
        """)
        frame_layout.addWidget(self.widgets['usuario_entry'])
        
        # Label Contraseña (sin cambios)
        self.widgets['contra_label'] = QLabel("Contraseña")
        self.widgets['contra_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial; border-radius: 15px; padding: 5px;
                min-width: 120px; min-height: 25px;
            }}
        """)
        self.widgets['contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['contra_label'])

        # Entry Contraseña (sin cambios)
        self.widgets['contra_entry'] = QLineEdit()
        self.widgets['contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry}; color: black; border-radius: 15px;
                padding: 6px 10px; min-width: 120px; min-height: 28px; font: 14px Arial;
            }}
        """)
        frame_layout.addWidget(self.widgets['contra_entry'])

        # Botones (sin cambios en su apariencia)
        self.widgets['btn_iniciar_sesion'] = QPushButton("Iniciar Sesión")
        # ... (Estilos de botones se mantienen igual) ...
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        # ... (Estilos de botones se mantienen igual) ...
        
        # Copia y pega los estilos de tus botones aquí para mantener la apariencia
        self.widgets['btn_iniciar_sesion'].setStyleSheet(f"QPushButton {{ background-color: {verde_boton}; border: none; border-radius: 18px; font: bold 14px Arial; padding: 8px; min-width: 140px; min-height: 30px; color: white;}} QPushButton:hover {{ background-color: {verde_oscuro}; }}")
        self.widgets['btn_volver'].setStyleSheet(f"QPushButton {{ background-color: {riesgo_medio}; border: none; border-radius: 18px; font: bold 14px Arial; padding: 8px; min-width: 140px; min-height: 30px; color: white;}} QPushButton:hover {{ background-color: {riesgo_alto}; }}")
        
        frame_layout.addWidget(self.widgets['btn_iniciar_sesion'])
        frame_layout.addWidget(self.widgets['btn_volver'])
        
        # Conexiones
        self.widgets['usuario_entry'].returnPressed.connect(self._iniciar_sesion)
        self.widgets['contra_entry'].returnPressed.connect(self._iniciar_sesion)
        self.widgets['btn_iniciar_sesion'].clicked.connect(self._iniciar_sesion)
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        
        main_layout.addWidget(self.frame)

    # << CAMBIO 3: _cargar_usuarios y _actualizar_vista ya NO son necesarios >>
    # Se pueden eliminar por completo estos métodos.

    def mostrar(self):
        # Limpiamos los campos al mostrar el formulario
        self.widgets['usuario_entry'].clear()
        self.widgets['contra_entry'].clear()
        self.show()

    def ocultar(self):
        self.hide()
        
    def _volver_atras(self):
        self.on_back()

    def _iniciar_sesion(self):
        # << CAMBIO 4: Lógica de inicio de sesión actualizada >>
        usuario = self.widgets['usuario_entry'].text().strip()
        if not usuario:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa tu nombre de usuario.")
            return
            
        contrasena = self.widgets['contra_entry'].text()
        if not contrasena:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa tu contraseña.")
            return
        
        # La llamada al servicio de autenticación ahora funciona con la API
        if self.auth_service.verificar_credenciales(usuario, contrasena):
            QMessageBox.information(self, "Éxito", f"Ha iniciado sesión como {usuario}")
            self.ocultar()
            self.on_success() # Llama a la función de éxito
        else:
            QMessageBox.warning(self, "Error de inicio de sesión", "Nombre de usuario o contraseña incorrectos.")