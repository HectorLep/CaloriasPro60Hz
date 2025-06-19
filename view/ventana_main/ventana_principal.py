#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal del Contador de Calorías con Login integrado
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QStackedWidget, 
                             QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon

# --- Imports Actualizados ---
from ..sidebar import Sidebar
from .welcome_screen import WelcomeScreen
from ..registrar_alimento import RegistrarAlimento
from ..agregar_alimento import AgregarAlimento
from ..grafico import Grafico
from ..historial import Historial
from ..salud.salud import Salud
from ..menu import Menu

# Importar los nuevos manejadores de formularios y servicios
from model.configuracion.servicios_usuario import UserService
from model.configuracion.mensajes import MessageHandler
from view.configuracion.formulario_usuario import UpdateUserForm
from view.configuracion.formulario_clave import PasswordForm
from view.configuracion.formulario_recordatorio import ReminderForm

# --- IMPORTS PARA EL LOGIN ---
# Asumiendo que tienes estos módulos adaptados a PyQt6
from view.login.login_form import LoginForm, IniciarSesionForm, RegistroForm
from model.login.auth_service import AuthService
from model.login.user_database import UserDatabase


# /view/ventana_main/ventana_principal.py

# --- Nueva Clase para la Pantalla de Login (REEMPLAZAR LA EXISTENTE) ---
class LoginScreen(QWidget):
    """
    Pantalla de login que se muestra antes de acceder a la aplicación principal.
    Gestiona el cambio entre los formularios de bienvenida, inicio de sesión y registro.
    """
    login_successful = pyqtSignal(str)  # Señal que emite el nombre de usuario

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.auth_service = AuthService()
        self.user_database = UserDatabase()

        # Guardaremos referencias a los formularios para no tener que crearlos cada vez
        self.login_form = None
        self.iniciar_sesion_form = None
        self.registro_form = None

        # Limpiar usuario al iniciar
        self.auth_service.limpiar_usuario_actual()
        self.init_ui()

    def init_ui(self):
        """Inicializar la interfaz de login"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #2b2b2b, stop:1 #3c3c3c);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Usaremos un StackedWidget para apilar los formularios de login
        self.form_stack = QStackedWidget(self)

        # --- Crear, conectar y añadir el formulario de bienvenida ---
        self.login_form = LoginForm(self, self.auth_service, self.on_login_success)
        
        # Conectar las señales de los botones a los métodos que cambian de vista
        self.login_form.iniciar_sesion_clicked.connect(self.mostrar_iniciar_sesion)
        self.login_form.registrarse_clicked.connect(self.mostrar_registro)

        self.form_stack.addWidget(self.login_form)
        layout.addWidget(self.form_stack)

    def mostrar_iniciar_sesion(self):
        """Crea (si no existe) y muestra el formulario de inicio de sesión."""
        if not self.iniciar_sesion_form:
            # El "on_success" de este formulario es el éxito final del login
            self.iniciar_sesion_form = IniciarSesionForm(self, self.auth_service, self.on_login_success, None)
            
            # Conectar la señal de "volver" para regresar al menú principal
            self.iniciar_sesion_form.volver_clicked.connect(self.mostrar_menu_login)
            self.form_stack.addWidget(self.iniciar_sesion_form)

        # Actualizar la lista de usuarios por si se registró uno nuevo
        self.iniciar_sesion_form.widgets['users_combobox'].clear()
        self.iniciar_sesion_form.widgets['users_combobox'].addItems(self.auth_service.obtener_usuarios())
        
        # Cambiar la vista al formulario de inicio de sesión
        self.form_stack.setCurrentWidget(self.iniciar_sesion_form)

    def mostrar_registro(self):
        """Crea (si no existe) y muestra el formulario de registro."""
        if not self.registro_form:
            # Cuando el registro es exitoso (on_success), lo llevamos a la pantalla de login
            self.registro_form = RegistroForm(self, self.auth_service, self.mostrar_iniciar_sesion, None)
            
            # Conectar la señal de "volver"
            self.registro_form.volver_clicked.connect(self.mostrar_menu_login)
            self.form_stack.addWidget(self.registro_form)

        # Cambiar la vista al formulario de registro
        self.form_stack.setCurrentWidget(self.registro_form)

    def mostrar_menu_login(self):
        """Vuelve a mostrar el formulario de login principal (botones de bienvenida)."""
        self.form_stack.setCurrentWidget(self.login_form)

    def on_login_success(self):
        """Callback cuando el login es exitoso. Emite la señal final."""
        usuario_actual = self.auth_service.obtener_usuario_actual()
        if usuario_actual:
            self.login_successful.emit(usuario_actual)

# --- Nueva Clase para la Pantalla de Configuración ---
class SettingsScreen(QWidget):
    """
    Nuevo widget que actúa como un menú para las diferentes 
    opciones de configuración.
    """
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.main_window = parent
        
        # Guardará una referencia al formulario de actualización de usuario
        self.update_user_form = None
        
        self.init_ui()

    def init_ui(self):
        # Layout principal de la pantalla de configuración
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        # Contenedor para los botones principales
        self.main_buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(self.main_buttons_widget)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botones de configuración
        self.btn_update_user = self.create_button("Actualizar Mis Datos", self.show_update_user_form)
        self.btn_update_password = self.create_button("Actualizar Contraseña", self.show_password_form)
        self.btn_reminders = self.create_button("Configurar Recordatorios", self.show_reminder_form)
        self.btn_delete_account = self.create_button("Eliminar Mi Cuenta", self.delete_account, "background-color: #e74c3c;") # Botón rojo
        
        # Botón para cerrar sesión
        self.btn_logout = self.create_button("Cerrar Sesión", self.logout, "background-color: #f39c12;") # Botón naranja

        buttons_layout.addWidget(self.btn_update_user)
        buttons_layout.addWidget(self.btn_update_password)
        buttons_layout.addWidget(self.btn_reminders)
        buttons_layout.addWidget(self.btn_delete_account)
        buttons_layout.addWidget(self.btn_logout)

        main_layout.addWidget(self.main_buttons_widget)
        
        # Instanciar el formulario de actualización de datos de usuario
        # Se le pasa 'self' como padre para que dibuje los widgets aquí
        # y un callback para restaurar la vista.
        self.update_user_form = UpdateUserForm(self, self.user_service, self.show_main_settings)
        # Ocultar los widgets de este formulario al inicio
        self.update_user_form.hide_widgets()

    def create_button(self, text, on_click, style="background-color: #3498db;"):
        """Función de ayuda para crear botones estandarizados."""
        button = QPushButton(text)
        button.setFixedSize(300, 50)
        button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                {style}
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        button.clicked.connect(on_click)
        return button

    def show_main_settings(self):
        """Muestra los botones principales y oculta los formularios."""
        if self.update_user_form:
            self.update_user_form.hide_widgets()
        self.main_buttons_widget.show()

    def show_update_user_form(self):
        """Muestra el formulario para actualizar datos de usuario."""
        self.main_buttons_widget.hide()
        if self.update_user_form:
            self.update_user_form.create_form()

    def show_password_form(self):
        """Lanza el diálogo para actualizar la contraseña."""
        password_dialog = PasswordForm(self, self.user_service)
        password_dialog.create_form()

    def show_reminder_form(self):
        """Lanza el diálogo para configurar recordatorios."""
        reminder_dialog = ReminderForm(self, self.user_service)
        reminder_dialog.create_form()
        
    def delete_account(self):
        """Inicia el proceso de eliminación de cuenta."""
        confirm = MessageHandler.confirmar_accion(
            "Confirmar Eliminación",
            "¿Estás seguro de que quieres eliminar tu cuenta? Esta acción es irreversible."
        )
        if confirm == "Sí":
            password, ok = QInputDialog.getText(
                self, 
                "Verificación de Seguridad", 
                "Por favor, introduce tu contraseña para confirmar:",
                QLineEdit.EchoMode.Password
            )
            if ok and password:
                if self.user_service.eliminar_usuario(password):
                    MessageHandler.mostrar_info("Cuenta Eliminada", "Tu cuenta ha sido eliminada con éxito.")
                    # Cierra la aplicación después de eliminar la cuenta
                    self.main_window.close()
                else:
                    MessageHandler.mostrar_advertencia("Error", "La contraseña es incorrecta. No se pudo eliminar la cuenta.")
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        confirm = MessageHandler.confirmar_accion(
            "Cerrar Sesión",
            "¿Estás seguro de que quieres cerrar la sesión actual?"
        )
        if confirm == "Sí":
            self.main_window.logout()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- Variables de estado ---
        self.current_user = None
        self.user_service = None
        self.is_logged_in = False
        
        # --- Stack principal para manejar login/main ---
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        # --- Inicializar interfaces ---
        self.init_login()
        self.init_main_ui()
        
        # Mostrar login inicialmente
        self.show_login()
        
    def init_login(self):
        """Inicializar la pantalla de login"""
        self.login_screen = LoginScreen(self)
        self.login_screen.login_successful.connect(self.on_login_success)
        self.main_stack.addWidget(self.login_screen)
        
    def init_main_ui(self):
        """Inicializar la interfaz principal (después del login)"""
        # Crear el widget principal
        self.main_widget = QWidget()
        self.main_stack.addWidget(self.main_widget)
        
        # Configurar la ventana
        self.setWindowTitle("Contador de Calorías Pro 60Hz")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
        """)
        
        # Layout principal
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear componentes (pero no los inicializar completamente hasta el login)
        self.sidebar = None
        self.content_area = None
        
    def setup_main_interface(self):
        """Configurar la interfaz principal después del login exitoso"""
        # Limpiar el layout existente
        layout = self.main_widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Crear sidebar
        self.sidebar = Sidebar()
        self.sidebar.section_changed.connect(self.change_section)
        
        # Crear área de contenido
        self.content_area = self.create_content_area()
        
        # Agregar al layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area, 1)
        
        # Configurar timer para fecha/hora
        self.setup_timer()
        
    def create_content_area(self):
        """Crear el área de contenido principal"""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border-left: 2px solid #4a4a4a;
            }
        """)
        
        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #3c3c3c;")
        
        # Crear todas las pantallas
        self.welcome_screen = WelcomeScreen()
        self.registrar_alimento = RegistrarAlimento()
        self.agregar_alimento = AgregarAlimento()
        self.grafico = Grafico()
        self.historial = Historial()
        self.settings = SettingsScreen(self.user_service, self)
        self.salud = Salud()
        self.menu = Menu()
        
        # Agregar al stack
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.registrar_alimento)
        self.stacked_widget.addWidget(self.agregar_alimento)
        self.stacked_widget.addWidget(self.grafico)
        self.stacked_widget.addWidget(self.historial)
        self.stacked_widget.addWidget(self.settings)
        self.stacked_widget.addWidget(self.salud)
        self.stacked_widget.addWidget(self.menu)
        
        layout.addWidget(self.stacked_widget)
        
        return content_frame
    
    def create_header(self):
        """Crear la barra superior"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-bottom: 2px solid #4a4a4a;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        title_label = QLabel("Contador de Calorías")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        
        # Mostrar usuario logueado
        user_label = QLabel(f"Usuario: {self.current_user}")
        user_label.setFont(QFont("Arial", 12))
        user_label.setStyleSheet("color: #cccccc;")
        
        layout.addWidget(title_label)
        layout.addWidget(user_label)
        layout.addStretch()
        
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Arial", 12))
        self.datetime_label.setStyleSheet("color: #cccccc;")
        self.update_datetime()
        
        layout.addWidget(self.datetime_label)
        
        return header
    
    def setup_timer(self):
        """Configurar el timer para actualizar fecha/hora"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
    
    def update_datetime(self):
        """Actualizar la fecha y hora en la interfaz"""
        now = datetime.now()
        formatted_date = now.strftime("Hoy es: %d-%m-%Y")
        if hasattr(self, 'datetime_label'):
            self.datetime_label.setText(formatted_date)
    
    def show_login(self):
        """Mostrar la pantalla de login"""
        self.main_stack.setCurrentWidget(self.login_screen)
        self.is_logged_in = False
    
    def show_main(self):
        """Mostrar la interfaz principal"""
        self.main_stack.setCurrentWidget(self.main_widget)
        self.is_logged_in = True
    
    def on_login_success(self, username):
        """Callback cuando el login es exitoso"""
        self.current_user = username
        self.user_service = UserService(self.current_user)
        
        # Configurar la interfaz principal
        self.setup_main_interface()
        
        # Mostrar la interfaz principal
        self.show_main()
        
        # Aquí puedes agregar lógica adicional como recordatorios
        # self.setup_recordatorios()
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        # Limpiar datos del usuario
        self.current_user = None
        self.user_service = None
        
        # Detener timer si existe
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Limpiar servicios de autenticación
        if hasattr(self.login_screen, 'auth_service'):
            self.login_screen.auth_service.limpiar_usuario_actual()
        
        # Mostrar login
        self.show_login()
    
    def change_section(self, section_name):
        """Cambiar de sección en la interfaz principal"""
        if not self.is_logged_in:
            return
            
        section_map = {
            "welcome": 0,
            "registrar": 1,
            "agregar": 2,
            "grafico": 3,
            "historial": 4,
            "settings": 5,
            "salud": 6,
            "menu": 7
        }
        
        if section_name in section_map:
            # Si cambiamos a la sección de settings, nos aseguramos de mostrar el menú principal
            if section_map[section_name] == 5:
                self.settings.show_main_settings()
            self.stacked_widget.setCurrentIndex(section_map[section_name])
    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()