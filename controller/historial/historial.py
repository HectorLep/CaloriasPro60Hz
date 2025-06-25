from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, 
                             QFrame, QLabel,QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

from view.historial.historial_view import HistorialView
from model.agregar_alimento import *
from controller.historial.historial_controller import HistorialController
from model.util.colores import *
from model.util.mensajes import *

class ModernStatusBar(QFrame):
    """Barra de estado moderna con indicadores"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(60)
        self.setStyleSheet("""
            ModernStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 0.8), stop:1 rgba(69, 160, 73, 0.8));
                border-radius: 15px;
                border: 2px solid rgba(76, 175, 80, 0.3);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Indicador de estado
        self.status_label = QLabel("🟢 Sistema Listo")
        self.status_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 14px;
        """)
        
        # Contador de registros
        self.records_label = QLabel("📊 Registros: 0")
        self.records_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 14px;
        """)
        
        # Indicador de conexión
        self.connection_label = QLabel("🔗 Conectado")
        self.connection_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 14px;
        """)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.records_label)
        layout.addStretch()
        layout.addWidget(self.connection_label)
        
        # Añadir sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def update_records_count(self, count):
        """Actualizar contador de registros"""
        self.records_label.setText(f"📊 Registros: {count:,}")
    
    def update_status(self, status, color="🟢"):
        """Actualizar estado del sistema"""
        self.status_label.setText(f"{color} {status}")
    
    def update_connection(self, connected=True):
        """Actualizar estado de conexión"""
        if connected:
            self.connection_label.setText("🔗 Conectado")
            self.connection_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
        else:
            self.connection_label.setText("❌ Desconectado")
            self.connection_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 14px;")

class WelcomeDialog(QMessageBox):
    """Diálogo de bienvenida moderno y atractivo"""
    def __init__(self, titulo, mensaje_html, parent=None): # Editado
        super().__init__(parent)
        self.setup_ui(titulo, mensaje_html) # Editado
        
    def setup_ui(self, titulo, mensaje_html): # Editado
        self.setWindowTitle(titulo) # Editado
        self.setIcon(QMessageBox.Icon.Information)
        
        # Ya no se usa la variable 'message' hardcodeada, se usa el parámetro
        self.setText(mensaje_html) # Editado
        
        # Estilo personalizado
        self.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafafa, stop:1 #f5f5f5);
                border-radius: 15px;
                min-width: 500px;
                max-width: 600px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
            }
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
        """)
        
        # Cambiar texto del botón
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        ok_button = self.button(QMessageBox.StandardButton.Ok)
        ok_button.setText("🚀 ¡Comenzar!")

class LoadingIndicator(QFrame):
    """Indicador de carga moderna"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.rotation = 0
        
    def setup_ui(self):
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            LoadingIndicator {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 50px;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.loading_label = QLabel("⏳")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            font-size: 30px;
            color: #4CAF50;
        """)
        layout.addWidget(self.loading_label)
        
    def start_animation(self):
        """Iniciar animación de carga"""
        self.animation_timer.start(100)
        self.show()
        
    def stop_animation(self):
        """Detener animación de carga"""
        self.animation_timer.stop()
        self.hide()
        
    def update_animation(self):
        """Actualizar animación"""
        loading_chars = ["⏳", "⌛", "🔄", "⚙️"]
        char_index = (self.rotation // 5) % len(loading_chars)
        self.loading_label.setText(loading_chars[char_index])
        self.rotation += 1

class Historial(QWidget):
    """Clase principal del historial con interfaz moderna y mejorada"""
    
    # Señales para comunicación
    datos_cargados = pyqtSignal(int)  # Emite el número de registros cargados
    error_ocurrido = pyqtSignal(str)  # Emite mensajes de error
    
    def __init__(self, panel_principal, color, usuario=None):
        super().__init__()
        self.panel_principal = panel_principal
        self.color = color
        self.usuario = usuario
        self.conn = None
        self.is_loading = False
        
        # Configuración inicial
        self.setup_ui()
        self.setup_controller()
        self.setup_connections()
        self.apply_modern_styling()
        
    def setup_ui(self):
        """Configura la interfaz de usuario moderna"""
        self.setObjectName('historial')
        
        # Layout principal con márgenes mejorados
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor principal con padding
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 0px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(15)
        
        # Barra de estado superior
        self.status_bar = ModernStatusBar()
        container_layout.addWidget(self.status_bar)
        
        # Indicador de carga (inicialmente oculto)
        self.loading_indicator = LoadingIndicator()
        self.loading_indicator.hide()
        
        # Vista del historial
        self.historial_view = HistorialView(self)
        container_layout.addWidget(self.historial_view)
        
        # Agregar el contenedor al layout principal
        main_layout.addWidget(container)
        
        # Posicionar indicador de carga en el centro
        self.loading_indicator.setParent(self)
        
    def setup_controller(self):
        """Configura el controlador y las conexiones"""
        try:
            self.status_bar.update_status("Inicializando controlador...", "🔄")
            
            self.historial_controller = HistorialController(self.usuario, self.historial_view)
            
            # Conectar señales del controlador si existen
            if hasattr(self.historial_controller, 'datos_actualizados'):
                self.historial_controller.datos_actualizados.connect(self.on_datos_actualizados)
            
            if hasattr(self.historial_controller, 'error_controlador'):
                self.historial_controller.error_controlador.connect(self.on_error_controlador)
            



            self.status_bar.update_status("Controlador listo", "🟢")
            
        except Exception as e:
            self.status_bar.update_status("Error en controlador", "🔴")
            self.show_error_message(f"Error al inicializar controlador: {str(e)}")

    def setup_connections(self):
        """Configurar conexiones de señales"""
        try:
            # Conectar señales de la vista
            if hasattr(self.historial_view, 'filtro_aplicado'):
                self.historial_view.filtro_aplicado.connect(self.aplicar_filtros)
            
            if hasattr(self.historial_view, 'filtros_limpiados'):
                self.historial_view.filtros_limpiados.connect(self.limpiar_filtros)
            
            if hasattr(self.historial_view, 'exportar_solicitado'):
                self.historial_view.exportar_solicitado.connect(self.exportar_datos)
            
            # Conectar filtros en tiempo real
            if hasattr(self.historial_view, 'search_input'):
                self.historial_view.search_input.textChanged.connect(self.filtrar_en_tiempo_real)
            
            if hasattr(self.historial_view, 'meal_filter'):
                self.historial_view.meal_filter.currentTextChanged.connect(self.filtrar_en_tiempo_real)
            
            # Conectar señales propias
            self.datos_cargados.connect(self.status_bar.update_records_count)
            self.error_ocurrido.connect(self.show_error_message)
            
        except Exception as e:
            print(f"Error al configurar conexiones: {e}")

    def apply_modern_styling(self):
        """Aplicar estilos modernos al widget principal"""
        self.setStyleSheet("""
            QWidget#historial {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 10px;
            }
        """)
        
        # Aplicar sombra al widget principal
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(25)
        shadow_effect.setColor(QColor(0, 0, 0, 30))
        shadow_effect.setOffset(0, 5)
        self.setGraphicsEffect(shadow_effect)

    def show_welcome_message(self):
        """Mostrar mensaje de bienvenida mejorado desde el archivo central."""
        try:
            info = MENSAJES.get("historial", {})
            titulo = info.get("titulo", "Bienvenido")
            mensaje_html = info.get("mensaje_html", "<p>Error al cargar mensaje.</p>")
            
            # Pasamos el título y el mensaje al crearlo
            welcome_dialog = WelcomeDialog(titulo, mensaje_html, self)
            welcome_dialog.exec()
            
            self.status_bar.update_status("¡Listo para usar!", "🎉")
            self.cargar_datos_inicial()
            
        except Exception as e:
            self.show_error_message(f"Error al mostrar bienvenida: {str(e)}")

    def cargar_datos_inicial(self):
        """Cargar datos iniciales con indicador de progreso"""
        self.start_loading("Cargando historial...")
        
        # Simular carga con timer (en implementación real, esto sería asíncrono)
        QTimer.singleShot(1500, self.finalizar_carga_inicial)

    def finalizar_carga_inicial(self):
        """Finalizar carga inicial de datos"""
        try:
            self.stop_loading()
            
            # Aquí iría la lógica real de carga de datos
            # Por ahora, emitir señal con datos simulados
            self.datos_cargados.emit(0)  # Se actualizará cuando el controlador cargue datos reales
            
            self.status_bar.update_status("Datos cargados correctamente", "✅")
            
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error al cargar datos: {str(e)}")

    def start_loading(self, message="Cargando..."):
        """Iniciar indicador de carga"""
        if not self.is_loading:
            self.is_loading = True
            self.status_bar.update_status(message, "🔄")
            
            # Centrar el indicador de carga
            self.center_loading_indicator()
            self.loading_indicator.start_animation()

    def stop_loading(self):
        """Detener indicador de carga"""
        if self.is_loading:
            self.is_loading = False
            self.loading_indicator.stop_animation()

    def center_loading_indicator(self):
        """Centrar el indicador de carga en el widget"""
        parent_rect = self.rect()
        indicator_rect = self.loading_indicator.rect()
        
        x = (parent_rect.width() - indicator_rect.width()) // 2
        y = (parent_rect.height() - indicator_rect.height()) // 2
        
        self.loading_indicator.move(x, y)

    def aplicar_filtros(self):
        """Aplicar filtros con feedback visual"""
        try:
            self.start_loading("Aplicando filtros...")
            
            # Delegar al controlador
            if hasattr(self.historial_controller, 'filtrar_por_fecha'):
                # CAMBIAR - Verificar si hay fechas antes de filtrar
                if hasattr(self.historial_view, 'date_from') and hasattr(self.historial_view, 'date_to'):
                    # Convertir fechas correctamente para PyQt6
                    try:
                        fecha_desde = self.historial_view.date_from.date().toString("yyyy-MM-dd")
                        fecha_hasta = self.historial_view.date_to.date().toString("yyyy-MM-dd")
                        
                        # Simular procesamiento
                        QTimer.singleShot(800, lambda: self._finalizar_filtros())
                    except Exception as date_error:
                        self.stop_loading()
                        self.show_error_message(f"Error con las fechas: {str(date_error)}")
                else:
                    QTimer.singleShot(800, lambda: self._finalizar_filtros())
            else:
                self.stop_loading()
                self.show_error_message("Función de filtrado no disponible")
                
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error al aplicar filtros: {str(e)}")
                
    def _finalizar_filtros(self):
        """Finalizar aplicación de filtros"""
        try:
            # CAMBIAR - Verificar antes de llamar al controlador
            if hasattr(self.historial_controller, 'filtrar_por_fecha'):
                # Solo llamar si el método existe y funciona
                try:
                    self.historial_controller.filtrar_por_fecha()
                except Exception as controller_error:
                    print(f"Error en controlador: {controller_error}")
                    # Continuar sin fallar
            
            self.stop_loading()
            self.status_bar.update_status("Filtros aplicados", "🔍")
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error en filtros: {str(e)}")
            
    def limpiar_filtros(self):
        """Limpiar filtros con animación"""
        try:
            self.start_loading("Limpiando filtros...")
            
            # Simular limpieza
            QTimer.singleShot(500, self._finalizar_limpieza)
            
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error al limpiar filtros: {str(e)}")

    def _finalizar_limpieza(self):
        """Finalizar limpieza de filtros"""
        try:
            # Aquí iría la lógica real de limpieza en el controlador
            self.stop_loading()
            self.status_bar.update_status("Filtros limpiados", "🧹")
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error en limpieza: {str(e)}")

    def filtrar_en_tiempo_real(self):
        """Filtrar datos en tiempo real mientras el usuario escribe"""
        # Implementar debounce para evitar filtros excesivos
        if hasattr(self, '_filter_timer'):
            self._filter_timer.stop()
        
        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self._ejecutar_filtro_tiempo_real)
        self._filter_timer.start(300)  # 300ms de delay

    def _ejecutar_filtro_tiempo_real(self):
        """Ejecutar filtro en tiempo real"""
        try:
            # CAMBIAR - Solo actualizar estado, no filtrar fechas aquí
            self.status_bar.update_status("Filtrando...", "🔍")
            
            # Resetear estado después de un tiempo
            QTimer.singleShot(1000, lambda: self.status_bar.update_status("Listo", "🟢"))
            
        except Exception as e:
            self.error_ocurrido.emit(f"Error en filtro tiempo real: {str(e)}")
            
    def exportar_datos(self):
        """Exportar datos con progreso visual"""
        try:
            self.start_loading("Preparando exportación...")
            
            # Simular preparación de exportación
            QTimer.singleShot(1000, self._realizar_exportacion)
            
        except Exception as e:
            self.stop_loading()
            self.error_ocurrido.emit(f"Error al exportar: {str(e)}")

    def _realizar_exportacion(self):
        """Realizar la exportación real"""
        try:
            self.stop_loading()
            
            # Delegar a la vista para la exportación
            if hasattr(self.historial_view, 'export_to_csv'):
                self.historial_view.export_to_csv()
                self.status_bar.update_status("Datos exportados", "📁")
            else:
                self.show_error_message("Función de exportación no disponible")
                
        except Exception as e:
            self.error_ocurrido.emit(f"Error en exportación: {str(e)}")

    def on_datos_actualizados(self, cantidad):
        """Callback cuando se actualizan los datos"""
        self.datos_cargados.emit(cantidad)
        self.status_bar.update_status("Datos actualizados", "🔄")

    def on_error_controlador(self, mensaje):
        """Callback para errores del controlador"""
        self.error_ocurrido.emit(mensaje)

    def show_error_message(self, mensaje):
        """Mostrar mensaje de error con estilo mejorado"""
        error_msg = QMessageBox(self)
        error_msg.setWindowTitle("⚠️ Error del Sistema")
        error_msg.setText(f"""
        <div style='padding: 15px;'>
            <h3 style='color: #f44336; margin-bottom: 15px;'>
                ❌ Se ha producido un error
            </h3>
            <p style='color: #333; font-size: 14px; line-height: 1.5;'>
                <b>Detalle del error:</b><br>
                {mensaje}
            </p>
            <div style='background: #ffebee; padding: 10px; border-radius: 5px; margin-top: 15px;'>
                <p style='color: #666; font-size: 12px; margin: 0;'>
                    💡 Si el problema persiste, contacta al administrador del sistema.
                </p>
            </div>
        </div>
        """)
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setStyleSheet("""
            QMessageBox {
                background-color: #fafafa;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        # Cambiar texto del botón
        error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        ok_button = error_msg.button(QMessageBox.StandardButton.Ok)
        ok_button.setText("🔧 Entendido")
        
        error_msg.exec()
        
        # Actualizar estado
        self.status_bar.update_status("Error reportado", "⚠️")

    def resizeEvent(self, event):
        """Manejar cambio de tamaño para reposicionar elementos"""
        super().resizeEvent(event)
        if hasattr(self, 'loading_indicator'):
            self.center_loading_indicator()

    def closeEvent(self, event):
        """Maneja el evento de cierre con limpieza mejorada"""
        try:
            # Mostrar indicador de cierre
            self.start_loading("Cerrando y limpiando...")
            
            # Limpiar recursos
            if hasattr(self, '_filter_timer'):
                self._filter_timer.stop()
            
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
            
            # Detener animaciones
            self.stop_loading()
            
            # Mensaje de despedida rápido
            self.status_bar.update_status("¡Hasta luego!", "👋")
            
            event.accept()
            
        except Exception as e:
            print(f"Error al cerrar: {e}")
            event.accept()

    def __del__(self):
        """Destructor mejorado de la clase"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except:
            pass