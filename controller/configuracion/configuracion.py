from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox,
                             QDialog, QLineEdit, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from controller.recordatorio.recordatorio_core import Recordatorio
from model.configuracion.servicios_usuario import UserService
from model.configuracion.mensajes import MessageHandler
from view.configuracion.formulario_usuario import UpdateUserForm
from view.configuracion.formulario_clave import PasswordForm
from view.configuracion.formulario_recordatorio import ReminderForm
from model.util.usuario_manager import BaseWidget
import os
import subprocess
import sys
import tempfile
import time
from model.util.colores import *

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
                font-size: 16px;
                font-style: italic;
                font-family: 'Times New Roman';
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)

class ConfigFrame(QFrame):
    """Frame personalizado para la configuración"""
    def __init__(self, width, height, bg_color="#2C3E50", parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 20px;
                padding: 5px;
            }}
        """)

class ConfigLabel(QLabel):
    """Label personalizado para mostrar información del usuario"""
    def __init__(self, text, color="white", font_size=12, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                background-color: transparent;
                padding: 2px;
            }}
        """)

class ConfigButton(QPushButton):
    """Botón personalizado para configuración"""
    def __init__(self, text, width=335, height=55, bg_color="#2ECC71", 
                 hover_color="#27AE60", text_color="#2C3E50", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 15px;
                font-size: 19px;
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

class DangerButton(QPushButton):
    """Botón de peligro personalizado"""
    def __init__(self, text, width=215, height=46, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #E74C3C;
                color: #2C3E50;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
            QPushButton:pressed {{
                background-color: #A93226;
            }}
        """)

class PasswordDialog(QDialog):
    """Diálogo para confirmar eliminación de cuenta"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Eliminación de Cuenta")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Ingresa tu contraseña")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 20))
        title_label.setStyleSheet("color: #2C3E50; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Campo de contraseña
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setFixedSize(250, 40)
        self.password_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 20px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
        """)
        
        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_layout.addWidget(self.password_entry)
        password_layout.addStretch()
        layout.addLayout(password_layout)
        
        # Botones
        self.confirm_btn = QPushButton("Confirmar Eliminación")
        self.confirm_btn.setFixedSize(200, 40)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(200, 40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Conectar señales
        self.cancel_btn.clicked.connect(self.reject)

class ConfigUI(QWidget, BaseWidget):
    def __init__(self, panel_principal, color, usuario=None):
        QWidget.__init__(self, panel_principal)
        BaseWidget.__init__(self, parent=panel_principal, usuario=usuario)
        
        self.panel_principal = panel_principal
        self.color = color
        self.usuario = usuario if usuario else self.get_current_user()
        self.user_service = UserService(self.usuario)
        self.recordatorio = Recordatorio(self.usuario)
        self.temp_dir = tempfile.mkdtemp()
        
        self.init_ui()
        self.setup_styles()
        self.mostrar_mensaje_inicial()

    def get_current_user(self):
        """Obtiene el usuario actual"""
        try:
            with open('usuario_actual.txt', 'r') as f:
                return f.read().strip()
        except:
            return "usuario_default"

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Configuración")
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame principal de fondo
        self.main_frame = ConfigFrame(750, 500, "#2C3E50")
        main_layout.addWidget(self.main_frame)
        
        # Layout dentro del frame principal
        content_layout = QVBoxLayout(self.main_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Botón de ayuda (esquina superior derecha)
        help_layout = QHBoxLayout()
        help_layout.addStretch()
        self.boton_ayuda = InfoButton("i")
        self.boton_ayuda.clicked.connect(self.mostrar_advertencia)
        help_layout.addWidget(self.boton_ayuda)
        help_layout.setContentsMargins(0, 15, 25, 0)
        content_layout.addLayout(help_layout)
        
        # Título
        self.create_title_section(content_layout)
        
        # Contenido principal
        self.create_main_content(content_layout)

    def create_title_section(self, parent_layout):
        """Crea la sección del título"""
        title_frame = ConfigFrame(680, 55, "#2ECC71")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.titulo_label = QLabel("Configuración")
        self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 27px;
                font-weight: bold;
                font-family: Arial;
                background-color: transparent;
            }
        """)
        title_layout.addWidget(self.titulo_label)
        
        # Contenedor para centrar el título
        title_container = QHBoxLayout()
        title_container.addStretch()
        title_container.addWidget(title_frame)
        title_container.addStretch()
        title_container.setContentsMargins(0, 10, 0, 0)
        
        parent_layout.addLayout(title_container)

    def create_main_content(self, parent_layout):
        """Crea el contenido principal"""
        content_container = QHBoxLayout()
        content_container.setSpacing(20)
        content_container.setContentsMargins(35, 10, 35, 10)
        
        # Panel izquierdo - Botones
        self.create_buttons_panel(content_container)
        
        # Panel derecho - Información del usuario
        self.create_user_info_panel(content_container)
        
        parent_layout.addLayout(content_container)
        parent_layout.addStretch()

    def create_buttons_panel(self, parent_layout):
        """Crea el panel de botones"""
        buttons_frame = ConfigFrame(390, 385, "#2C3E50")
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(50)
        buttons_layout.setContentsMargins(30, 50, 30, 30)
        
        # Botón actualizar información
        self.guardar_button = ConfigButton("Actualizar información")
        self.guardar_button.clicked.connect(self.mostrar_interfaz_guardar)
        buttons_layout.addWidget(self.guardar_button)
        
        # Botón actualizar contraseña
        self.mostrar_contra_button = ConfigButton("Actualizar Contraseña")
        self.mostrar_contra_button.clicked.connect(self.mostrar_formulario_contrasena)
        buttons_layout.addWidget(self.mostrar_contra_button)
        
        # Botón configurar recordatorio
        self.config_peso_button = ConfigButton("Configurar Recordatorio Peso", width=310)
        self.config_peso_button.clicked.connect(self.mostrar_formulario_recordatorio)
        buttons_layout.addWidget(self.config_peso_button)
        
        buttons_layout.addStretch()
        parent_layout.addWidget(buttons_frame)

    def create_user_info_panel(self, parent_layout):
        """Crea el panel de información del usuario"""
        # Frame exterior claro
        outer_frame = ConfigFrame(215, 260, "#95A5A6")
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame interior oscuro
        inner_frame = ConfigFrame(195, 240, "#2C3E50")
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setSpacing(15)
        inner_layout.setContentsMargins(15, 15, 15, 15)
        
        # Cargar datos del usuario
        self.load_user_data(inner_layout)
        
        # Botones de sesión
        self.create_session_buttons(inner_layout)
        
        outer_layout.addWidget(inner_frame)
        parent_layout.addWidget(outer_frame)

    def load_user_data(self, layout):
        """Carga y muestra los datos del usuario"""
        try:
            edad, genero, peso, nivel_actividad, meta_cal, estatura = self.user_service.cargar_datos_usuario()
            
            self.nombre_label = ConfigLabel(f"Nombre: {self.usuario}")
            self.edad_label = ConfigLabel(f"Edad: {edad}")
            self.genero_label = ConfigLabel(f"Género: {genero}")
            self.peso_label = ConfigLabel(f"Peso: {peso} kg")
            self.estatura_label = ConfigLabel(f"Estatura: {estatura} cm")
            self.obj_calorias_label = ConfigLabel(f"Objetivo de Calorías: {meta_cal}")
            self.lvl_actividad_label = ConfigLabel(f"Nivel de Actividad: {nivel_actividad}")
            
            layout.addWidget(self.nombre_label)
            layout.addWidget(self.edad_label)
            layout.addWidget(self.genero_label)
            layout.addWidget(self.peso_label)
            layout.addWidget(self.estatura_label)
            layout.addWidget(self.obj_calorias_label)
            layout.addWidget(self.lvl_actividad_label)
            
        except Exception as e:
            error_label = ConfigLabel(f"Error al cargar datos: {str(e)}", color="#E74C3C")
            layout.addWidget(error_label)

    def create_session_buttons(self, layout):
        """Crea los botones de sesión"""
        layout.addStretch()
        
        # Botón cerrar sesión
        self.cerrar_sesion_button = DangerButton("Cerrar Sesión")
        self.cerrar_sesion_button.clicked.connect(self.cerrar_sesion)
        layout.addWidget(self.cerrar_sesion_button)
        
        # Botón borrar cuenta
        self.borrar_cuenta_button = DangerButton("Borrar Cuenta")
        self.borrar_cuenta_button.clicked.connect(self.ventana_borrar_cuenta)
        layout.addWidget(self.borrar_cuenta_button)

    def setup_styles(self):
        """Configura los estilos generales"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ECF0F1;
                font-family: Arial;
            }
        """)

    def mostrar_mensaje_inicial(self):
        """Muestra mensaje inicial"""
        QTimer.singleShot(1000, lambda: self.mostrar_mensaje(
            "Esta es la pestaña de configuracion, dentro podras configurar todo lo que es tu perfil como el objetivo de calorias y el nivel de actividad",
            "Configuracion"
        ))

    def mostrar_mensaje(self, mensaje, titulo):
        """Muestra un mensaje informativo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def mostrar_advertencia(self):
        """Muestra la advertencia de información"""
        self.mostrar_mensaje(
            "Esta es la pestaña de configuracion, dentro podras configurar todo lo que es tu perfil como el objetivo de calorias y el nivel de actividad.",
            "Configuracion"
        )

    def mostrar_interfaz_guardar(self):
        """Muestra la interfaz para guardar datos"""
        self.guardar_button.setEnabled(False)
        self.mostrar_contra_button.setEnabled(False)
        self.config_peso_button.setEnabled(False)
        
        try:
            self.form_handler = UpdateUserForm(self, self.user_service, self.restaurar_interfaz_actualizar_info)
            self.form_handler.create_form()
        except Exception as e:
            self.mostrar_error(f"Error al abrir formulario: {str(e)}")
            self.restaurar_interfaz_actualizar_info()

    def mostrar_formulario_contrasena(self):
        """Muestra el formulario de contraseña"""
        try:
            self.form_handler = PasswordForm(self.panel_principal, self.user_service)
            self.form_handler.create_form()
        except Exception as e:
            self.mostrar_error(f"Error al abrir formulario de contraseña: {str(e)}")

    def mostrar_formulario_recordatorio(self):
        """Muestra el formulario de recordatorio"""
        try:
            self.form_handler = ReminderForm(self.panel_principal, self.user_service)
            self.form_handler.create_form()
        except Exception as e:
            self.mostrar_error(f"Error al abrir formulario de recordatorio: {str(e)}")

    def restaurar_interfaz_actualizar_info(self):
        """Restaura la interfaz después de actualizar información"""
        self.guardar_button.setEnabled(True)
        self.mostrar_contra_button.setEnabled(True)
        self.config_peso_button.setEnabled(True)
        
        # Recargar datos del usuario
        try:
            # Limpiar el layout de información del usuario y recargar
            self.recreate_user_info()
        except Exception as e:
            print(f"Error al recargar datos: {e}")

    def recreate_user_info(self):
        """Recrea la información del usuario"""
        # Esta función debería actualizar solo la sección de información del usuario
        # Por simplicidad, se puede recrear toda la interfaz o solo actualizar los labels
        pass

    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        reply = QMessageBox.question(
            self, 
            "Cerrar Sesión",
            "¿Estás seguro de que deseas cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mostrar_mensaje("Sesión cerrada.", "Cerrar sesión")
            QTimer.singleShot(2000, self.reiniciar_aplicacion)

    def ventana_borrar_cuenta(self):
        """Abre la ventana para borrar cuenta"""
        dialog = PasswordDialog(self)
        dialog.confirm_btn.clicked.connect(lambda: self.eliminar_cuenta(dialog))
        dialog.exec()

    def eliminar_cuenta(self, dialog):
        """Elimina la cuenta del usuario"""
        contra_ingresada = dialog.password_entry.text()
        
        if not contra_ingresada:
            self.mostrar_error("Por favor ingresa tu contraseña.")
            return
        
        try:
            exito = self.user_service.eliminar_usuario(contra_ingresada)
            
            if not exito:
                self.mostrar_error("La contraseña es incorrecta.")
                return
            
            # Confirmación final
            reply = QMessageBox.question(
                self,
                "Última Confirmación",
                "¿REALMENTE estás seguro de eliminar tu cuenta? Todos tus datos se perderán.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                dialog.reject()
                return
            
            # Limpiar archivo de usuario actual
            with open('usuario_actual.txt', 'w') as f:
                f.write('')
            
            self.mostrar_mensaje("Cuenta eliminada. La aplicación se cerrará.", "Éxito")
            dialog.accept()
            QTimer.singleShot(2000, self.reiniciar_aplicacion)
            
        except Exception as e:
            self.mostrar_error(f"Error al eliminar cuenta: {str(e)}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()

    def reiniciar_aplicacion(self):
        """Reinicia la aplicación"""
        try:
            QApplication.quit()
            time.sleep(1)
            python = sys.executable
            script_path = os.path.abspath("main.py")
            subprocess.Popen([python, script_path])
            sys.exit()
        except Exception as e:
            print(f"Error al reiniciar aplicación: {e}")
            sys.exit()

# Función de compatibilidad si se necesita
def mensage(self, mensaje, titulo):
    """Función de compatibilidad para mostrar mensajes"""
    self.mostrar_mensaje(mensaje, titulo)