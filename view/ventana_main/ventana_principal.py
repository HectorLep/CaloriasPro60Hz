#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal del Contador de Calorías con Login integrado
"""
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from model.grafico.database_manager import ChartDataManager
from view.grafico.grafico_view import GraficoView
from ..sidebar import Sidebar
from .welcome_screen import WelcomeScreen
from ..menu import Menu
from view.salud.salud import Salud
from controller.configuracion.configuracion import ConfigUI
from view.login.login_form import LoginForm
from view.login.iniciar_sesion_form import IniciarSesionForm
from view.login.registro_form import RegistroForm
from model.login.auth_service import AuthService
from model.login.user_database import UserDatabase
from model.util.base import DBManager
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
        self.current_user = None
        self.is_logged_in = False
        self.welcome_message_flags = {} # Caché en memoria para evitar lecturas repetidas de la BD
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        # Inicializar interfaces    
        self.init_login()
        self.init_main_ui()
        
        # Mostrar login inicialmente
        self.show_login()

    def check_message_status(self, section_name):
        """Verifica en la BD del USUARIO si el mensaje para una sección ya se mostró."""
        conn = None
        if not self.current_user:
            return 0 # Si no hay un usuario logueado, no se puede verificar.

        try:
            # --- CAMBIO CLAVE ---
            # Conectamos a la base de datos del usuario actual, no a la principal.
            # Es posible que tu método se llame diferente (ej: conectar_bd_usuario).
            # Asegúrate de que el nombre del método sea el correcto.
            conn = DBManager.conectar_usuario(self.current_user) 
            
            query = f"SELECT {section_name} FROM mensajes LIMIT 1"
            resultado = DBManager.ejecutar_query(conn, query)
            
            if resultado and resultado[0] is not None:
                return resultado[0]
            return 0
        except sqlite3.Error as e:
            # Este error puede ocurrir si la tabla 'mensajes' aún no existe para un usuario.
            print(f"NOTA: No se pudo verificar el estado del mensaje para '{section_name}'. Error: {e}")
            return 0 # Fallamos de forma segura, asumiendo que el mensaje no se ha mostrado.
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)

    def update_message_status(self, section_name):
        """Actualiza en la BD del USUARIO el estado de un mensaje a 'mostrado' (1)."""
        conn = None
        if not self.current_user:
            return # Si no hay un usuario logueado, no se puede actualizar.

        try:
            # --- CAMBIO CLAVE ---
            # De nuevo, nos aseguramos de conectar a la base de datos del usuario.
            conn = DBManager.conectar_usuario(self.current_user) 
            
            query = f"UPDATE mensajes SET {section_name} = 1"
            DBManager.ejecutar_query(conn, query, commit=True)
        except sqlite3.Error as e:
            print(f"Error al actualizar estado del mensaje para '{section_name}': {e}")
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)
                

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
        
        self.agregar_alimento = Agregar_Alimento(
            panel_principal=self.stacked_widget,
            color="#3c3c3c",
            usuario=self.current_user
        )
        
        # --- INICIO DEL CAMBIO IMPORTANTE ---
        # 1. Creamos una única instancia del gestor de datos
        self.data_manager = ChartDataManager(username=self.current_user)

        # 2. Creamos la nueva vista del gráfico, inyectando el gestor de datos
        self.graficos_view = GraficoView(data_provider=self.data_manager)
        # --- FIN DEL CAMBIO IMPORTANTE ---

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
        # self.grafico = Grafico() <-- Se elimina esta línea
        self.stacked_widget.addWidget(self.graficos_view) # <-- Se añade la nueva vista
        self.stacked_widget.addWidget(self.historial)
        self.stacked_widget.addWidget(self.settings)
        self.stacked_widget.addWidget(self.salud)
        self.stacked_widget.addWidget(self.menu)
        
        layout.addWidget(self.stacked_widget)
        self.conectar_modulos()

        return content_frame
    
    def conectar_modulos(self):
        """Conecta las señales de los diferentes módulos a los slots de otros."""
        print("Realizando conexiones entre módulos...")

        if hasattr(self.agregar_alimento, 'catalogo_alimentos_actualizado') and \
           hasattr(self.registrar_alimento, 'refrescar_lista_alimentos'):
            
            self.agregar_alimento.catalogo_alimentos_actualizado.connect(
                self.registrar_alimento.refrescar_lista_alimentos
            )
            print("CONEXIÓN CREADA: Agregar Alimento -> Registrar Alimento (ComboBox)")

        # --- OTRAS CONEXIONES ÚTILES QUE PREPARAMOS ---
        # Cuando se registra un consumo diario...
        if hasattr(self.registrar_alimento, 'consumo_diario_actualizado'):
            # ... se refresca la vista del Historial.
            if hasattr(self.historial, 'refrescar_vista'):
                self.registrar_alimento.consumo_diario_actualizado.connect(
                    self.historial.refrescar_vista
                )
                print("CONEXIÓN CREADA: Registrar Alimento -> Historial")
            
            # ... y también se refresca la vista de Salud (para el progreso de calorías).
            if hasattr(self.salud, 'refrescar_vista'):
                self.registrar_alimento.consumo_diario_actualizado.connect(
                    self.salud.refrescar_vista
                )
                print("CONEXIÓN CREADA: Registrar Alimento -> Salud")

        # 4. Cuando Configuración actualiza los datos del usuario...
        # ... se refresca la vista de Salud.
        if hasattr(self.settings, 'datos_usuario_actualizados') and hasattr(self.salud, 'refrescar_vista'):
            self.settings.datos_usuario_actualizados.connect(
                self.salud.refrescar_vista
            )
            print("CONEXIÓN CREADA: Configuración -> Salud")

        # 5. Y cuando Salud actualiza datos (ej: el peso)...
        # ... se refresca la vista de Configuración.
        if hasattr(self.salud, 'datos_usuario_actualizados') and hasattr(self.settings, 'refrescar_vista'):
            self.salud.datos_usuario_actualizados.connect(
                self.settings.refrescar_vista
            )
            print("CONEXIÓN CREADA: Salud -> Configuración")


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
        self.sidebar.set_usuario(self.current_user)
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
            """Cambiar de sección y mostrar mensaje de bienvenida una sola vez."""
            if not self.is_logged_in:
                return
                
            # Diccionario que mapea nombres de sección a sus widgets, métodos y columnas de BD
            section_details = {
                "salud": {
                    "widget": self.salud, 
                    "welcome_method": "mostrar_mensaje_bienvenida",
                    "db_column": "salud"
                },
                "historial": {
                    "widget": self.historial, 
                    "welcome_method": "show_welcome_message",
                    "db_column": "historial"
                },
                "registrar": {
                    "widget": self.registrar_alimento, 
                    "welcome_method": "mostrar_mensaje_bienvenida",
                    "db_column": "registrar_alimento"
                },
                "settings": {
                    "widget": self.settings,
                    "welcome_method": "mostrar_mensaje_inicial",
                    "db_column": "configuracion"
                },
                "agregar": {
                    "widget": self.agregar_alimento,
                    "welcome_method": "_mostrar_mensaje_bienvenida",
                    "db_column": "agregar_alimento"
                }
            }

            if section_name in section_details:
                details = section_details[section_name]
                db_column_name = details["db_column"]

                if db_column_name not in self.welcome_message_flags:
                    status = self.check_message_status(db_column_name)
                    self.welcome_message_flags[db_column_name] = status

                if self.welcome_message_flags[db_column_name] == 0:
                    widget = details["widget"]
                    method_name = details["welcome_method"]
                    
                    if hasattr(widget, method_name):
                        welcome_method = getattr(widget, method_name)
                        welcome_method()
                    
                    self.update_message_status(db_column_name)
                    self.welcome_message_flags[db_column_name] = 1

            # Lógica para cambiar de vista. El índice de 'grafico' (3) ahora corresponde a 'graficos_view'
            section_map = {
                "welcome": 0, "registrar": 1, "agregar": 2, "grafico": 3,
                "historial": 4, "settings": 5, "salud": 6, "menu": 7
            }
            
            if section_name in section_map:
                self.stacked_widget.setCurrentIndex(section_map[section_name])
                                                    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()