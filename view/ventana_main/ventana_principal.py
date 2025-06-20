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
from ..sidebar import Sidebar
from .welcome_screen import WelcomeScreen
from ..grafico import Grafico
from ..salud.salud import Salud
from ..menu import Menu
from controller.configuracion.configuracion import ConfigUI
from view.login.login_form import LoginForm, IniciarSesionForm, RegistroForm
from model.login.auth_service import AuthService
from model.login.user_database import UserDatabase
from view.agregar_alimento.agregar_alimento import Agregar_Alimento
from controller.registrar_alimento.registrar_alimento import RegistroAlimentoPyQt6
from controller.historial.historial import Historial

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- Variables de estado ---
        self.current_user = None
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
        self.registrar_alimento = RegistroAlimentoPyQt6(usuario=self.current_user)
        
        # INSTANCIACIÓN CORREGIDA DE AGREGAR ALIMENTO
        # Pasamos los parámetros requeridos: panel_principal, color, usuario
        self.agregar_alimento = Agregar_Alimento(
            panel_principal=self.stacked_widget,
            color="#3c3c3c",
            usuario=self.current_user
        )
        
        self.grafico = Grafico()
        # Por esta:
        self.historial = Historial(
            panel_principal=self.stacked_widget,
            color="#3c3c3c", 
            usuario=self.current_user
)
        self.settings = ConfigUI(self, "#3c3c3c", self.current_user)
        
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
        self.setup_main_interface()
        
        # Mostrar la interfaz principal
        self.show_main()
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        # Limpiar datos del usuario
        self.current_user = None
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
            self.stacked_widget.setCurrentIndex(section_map[section_name])
    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()