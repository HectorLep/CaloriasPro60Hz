from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFrame, QMessageBox)
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
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Frame contenedor
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
        # Espaciado mínimo entre widgets
        frame_layout.setSpacing(6)

        # Título
        titulo = QLabel("Iniciar Sesión")
        # Reducimos el tamaño de la fuente del título
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro}; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)

        # Label Usuario
        self.widgets['users_label'] = QLabel("Usuario")
        self.widgets['users_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial;
                border-radius: 15px;
                padding: 5px;
                min-width: 120px;
                min-height: 25px;
            }}
        """)
        self.widgets['users_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['users_label'])

        # ComboBox Usuario
        self.widgets['users_combobox'] = QComboBox()
        self.widgets['users_combobox'].setStyleSheet(f"""
            QComboBox {{
                background-color: {gris_label}; color: black; border-radius: 15px;
                padding: 5px 10px;
                min-width: 120px;
                min-height: 28px;
                font: 14px Arial;
            }}
            QComboBox::drop-down {{ background-color: {verde_boton}; border-radius: 7px; }}
            QComboBox::drop-down:hover {{ background-color: {verde_oscuro}; }}
        """)
        frame_layout.addWidget(self.widgets['users_combobox'])
        
        # Label Contraseña
        self.widgets['contra_label'] = QLabel("Contraseña")
        self.widgets['contra_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; color: white;
                font: bold 14px Arial;
                border-radius: 15px;
                padding: 5px;
                min-width: 120px;
                min-height: 25px;
            }}
        """)
        self.widgets['contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['contra_label'])

        # Entry Contraseña
        self.widgets['contra_entry'] = QLineEdit()
        self.widgets['contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry}; color: black; border-radius: 15px;
                padding: 6px 10px;
                min-width: 120px;
                min-height: 28px;
                font: 14px Arial;
            }}
        """)
        frame_layout.addWidget(self.widgets['contra_entry'])

        # Botón Iniciar Sesión
        self.widgets['btn_iniciar_sesion'] = QPushButton("Iniciar Sesión")
        btn_iniciar_palette = self.widgets['btn_iniciar_sesion'].palette()
        btn_iniciar_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_iniciar_sesion'].setPalette(btn_iniciar_palette)
        self.widgets['btn_iniciar_sesion'].setStyleSheet(f"""
            QPushButton {{
                background-color: {verde_boton}; border: none; border-radius: 18px;
                font: bold 14px Arial;
                padding: 8px;
                min-width: 140px;
                min-height: 30px;
            }}
            QPushButton:hover {{ background-color: {verde_oscuro}; }}
        """)
        frame_layout.addWidget(self.widgets['btn_iniciar_sesion'])
        
        # Botón Volver (siempre visible)
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        btn_volver_palette = self.widgets['btn_volver'].palette()
        btn_volver_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_volver'].setPalette(btn_volver_palette)
        self.widgets['btn_volver'].setStyleSheet(f"""
            QPushButton {{
                background-color: {riesgo_medio}; border: none; border-radius: 18px;
                font: bold 14px Arial;
                padding: 8px;
                min-width: 140px;
                min-height: 30px;
            }}
            QPushButton:hover {{ background-color: {riesgo_alto}; }}
        """)
        frame_layout.addWidget(self.widgets['btn_volver'])
        
        # Conexiones de los botones (Esta sección causó el error)
        self.widgets['contra_entry'].returnPressed.connect(self._iniciar_sesion)
        self.widgets['btn_iniciar_sesion'].clicked.connect(self._iniciar_sesion)
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        
        main_layout.addWidget(self.frame)

    def _cargar_usuarios(self):
        try:
            usuarios = self.auth_service.obtener_usuarios()
            self.widgets['users_combobox'].clear()
            if not usuarios:
                self.widgets['users_combobox'].addItem("No hay usuarios registrados")
                self.widgets['users_combobox'].setEnabled(False)
            else:
                self.widgets['users_combobox'].addItems(usuarios)
                self.widgets['users_combobox'].setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar usuarios: {str(e)}")

    def _actualizar_vista(self):
        hay_usuarios = self.widgets['users_combobox'].isEnabled()
        
        self.widgets['contra_label'].setVisible(hay_usuarios)
        self.widgets['contra_entry'].setVisible(hay_usuarios)
        self.widgets['btn_iniciar_sesion'].setVisible(hay_usuarios)
        
        self.adjustSize()
        self.layout().activate()

    def mostrar(self):
        self._cargar_usuarios()
        self._actualizar_vista()
        self.show()

    def ocultar(self):
        self.hide()
        
    def _volver_atras(self):
        self.volver_clicked.emit()

    # --- MÉTODO FALTANTE ---
    # Este es el método que causaba el error. Asegúrate de que esté aquí.
    def _iniciar_sesion(self):
        usuario = self.widgets['users_combobox'].currentText()
        if not usuario or usuario == "No hay usuarios registrados":
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un usuario válido.")
            return
            
        contrasena = self.widgets['contra_entry'].text()
        if not contrasena:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa tu contraseña.")
            return
        
        try:
            if self.auth_service.verificar_credenciales(usuario, contrasena):
                if self.auth_service.guardar_usuario_actual(usuario):
                    QMessageBox.information(self, "Éxito", f"Ha iniciado sesión como {usuario}")
                    self.ocultar()
                    self.on_success()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la sesión actual.")
            else:
                QMessageBox.warning(self, "Advertencia", "Contraseña incorrecta.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sesión: {str(e)}")
