from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
# from model.util.base import DBManager # Eliminado
from PyQt6.QtWidgets import QMessageBox # Asegurar que QMessageBox está importado

class Peso(QDialog):
    # Señal para notificar cuando se actualiza el peso
    peso_actualizado = pyqtSignal()
    
    # def __init__(self, parent=None, usuario="default_user", callback=None): # Firma original
    def __init__(self, parent=None, api_client=None, callback=None): # Nueva firma
        super().__init__(parent)
        # self.usuario = usuario # Eliminado
        self.api_client = api_client
        self.callback = callback
        
        if not self.api_client:
            # Esto es un problema crítico, el diálogo no puede funcionar sin el cliente API.
            # Podríamos deshabilitar todo o mostrar un error inmediato.
            # Por ahora, se asumirá que siempre se pasa un api_client válido.
            print("ERROR CRÍTICO: Peso dialog iniciado sin api_client.")
            # Considerar cerrar o mostrar error aquí. QMessageBox.critical(self, "Error", "Error interno: No se proporcionó cliente API.")
            # self.close()
            # return

        self.setWindowTitle('Actualizar peso')
        self.setFixedSize(400, 270)
        self.setModal(True)  # Equivalente a attributes('-topmost', True)
        
        # Configurar el diseño
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Label de peso actual
        self.peso_actual_label = QLabel(self.get_peso())
        self.peso_actual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.peso_actual_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(self.peso_actual_label)
        
        # Espaciador
        main_layout.addSpacing(20)
        
        # Label de instrucción
        self.peso_label = QLabel("Ingrese su peso actual")
        self.peso_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.peso_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(self.peso_label)
        
        # Entry para el peso
        self.peso_entry = QLineEdit()
        self.peso_entry.setPlaceholderText("Ejemplo: 70.5")
        self.peso_entry.returnPressed.connect(self.registrar_peso)  # Enter para registrar
        main_layout.addWidget(self.peso_entry)
        
        # Botón de registrar
        self.guardar_button = QPushButton("Registrar")
        self.guardar_button.clicked.connect(self.registrar_peso)
        main_layout.addWidget(self.guardar_button)
        
        # Espaciador al final
        main_layout.addStretch()
        
    def setup_styles(self):
        """Configura los estilos de los elementos"""
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: white;
            }
        """)
        
        # Estilo del label de peso actual
        self.peso_actual_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
                background-color: #34495E;
                border-radius: 10px;
                margin: 10px 0px;
            }
        """)
        
        # Estilo del label de instrucción
        self.peso_label.setStyleSheet("""
            QLabel {
                color: #3498DB;
                background-color: #34495E;
                padding: 10px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        
        # Estilo del campo de entrada
        self.peso_entry.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        
        # Estilo del botón
        self.guardar_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: #34495E;
                border: none;
                border-radius: 15px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
    
    def validate_weight_change(self, new_weight_kg: float) -> bool:
        """
        Valida si el nuevo peso es razonable comparado con el peso actual en la API.
        La lógica de fechas y umbrales diarios/mensuales se simplifica
        ya que la API actual no provee historial de pesos.
        """
        if not self.api_client: return False # No se puede validar

        try:
            user_data = self.api_client.get_user_profile()
            if not user_data or 'peso' not in user_data:
                # No hay peso previo en la API o error al obtenerlo, aceptar el nuevo peso.
                return True
            
            previous_weight_kg = user_data['peso']
            if previous_weight_kg is None: # Podría ser que el campo exista pero sea None
                 return True

            weight_diff = abs(new_weight_kg - previous_weight_kg)
            
            # Umbral de cambio significativo general (ej. 15kg)
            significant_change_threshold = 15
            
            if weight_diff > significant_change_threshold:
                reply = QMessageBox.question(
                    self,
                    "Confirmar Peso",
                    f"El peso ingresado ({new_weight_kg} kg) indica un cambio significativo de {weight_diff:.1f} kg "
                    f"respecto a su peso actual registrado en el perfil ({previous_weight_kg} kg). "
                    f"¿Es correcto este valor?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                return reply == QMessageBox.StandardButton.Yes
            
            return True  # Cambio dentro del umbral
            
        except Exception as e:
            print(f"Error al validar peso con la API: {e}")
            QMessageBox.critical(self, "Error de Validación",
                                 "No se pudo validar el peso con el servidor. Por favor, intente de nuevo.")
            return False

    def registrar_peso(self):
        """Registra el nuevo peso actualizando el perfil del usuario vía API."""
        if not self.api_client:
            QMessageBox.critical(self, "Error", "Funcionalidad no disponible (sin cliente API).")
            return

        peso_texto = self.peso_entry.text().strip().replace(',', '.')
        
        if not peso_texto:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese un peso.")
            return
        
        try:
            nuevo_peso_kg = float(peso_texto)
            
            if not (0 < nuevo_peso_kg <= 500): # Rango de peso razonable
                QMessageBox.warning(self, "Advertencia", "Ingrese un peso válido (entre 0 y 500 kg).")
                return
            
            if not self.validate_weight_change(nuevo_peso_kg):
                return  # Validación fallida o el usuario canceló

            # --- Interacción con la API ---
            # IMPORTANTE: La API actual (controller/API/user/api.py) NO TIENE un endpoint
            # para actualizar el perfil del usuario (ej. PUT /users/me/).
            # El siguiente código asume que api_client.update_user_profile({'peso': nuevo_peso_kg})
            # realizaría dicha llamada. Si el endpoint no existe, esto fallará.
            
            print(f"INFO: Intentando actualizar peso a {nuevo_peso_kg} kg vía API.")
            try:
                # Asumiendo que el api_client tiene un método para actualizar el perfil,
                # y que el endpoint PUT /users/me/ o similar existe y acepta {'peso': ...}
                self.api_client.update_user_profile({'peso': nuevo_peso_kg})
                
                QMessageBox.information(self, "Éxito", "Peso actualizado correctamente en su perfil.")
                self.peso_actualizado.emit()
                if self.callback:
                    self.callback()
                self.accept() # Cerrar diálogo
            
            except AttributeError: # Si api_client no tiene update_user_profile
                 QMessageBox.critical(self, "Error de Desarrollo",
                                     "La función para actualizar el perfil no está implementada en el cliente API.")
            except Exception as api_error: # Captura errores de red, HTTP 4xx/5xx de la API, etc.
                print(f"Error de API al registrar peso: {api_error}")
                # Aquí se podría verificar el status code si la excepción es de requests
                # Por ejemplo, si es un 404 o 405 podría indicar que el endpoint no existe.
                # if isinstance(api_error, requests.exceptions.HTTPError) and api_error.response.status_code in [404, 405]:
                #     msg = "La funcionalidad para actualizar el peso en el servidor no está disponible."
                # else:
                #     msg = "Error al comunicar con el servidor para actualizar el peso."
                QMessageBox.critical(self, "Error de API", f"No se pudo actualizar el peso en el servidor: {api_error}")

        except ValueError:
            QMessageBox.warning(self, "Advertencia", "Ingrese un peso válido (solo números).")
        except Exception as e: # Otros errores inesperados
            QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error al procesar el peso: {e}")
            print(f"Error inesperado en registrar_peso: {e}")

    def get_peso(self) -> str:
        """Obtiene el último peso registrado desde el perfil de la API."""
        if not self.api_client:
            return "Cliente API no disponible."
        try:
            user_data = self.api_client.get_user_profile() # Método hipotético
            if user_data and 'peso' in user_data and user_data['peso'] is not None:
                peso_kg = user_data['peso']
                # La API no proporciona fecha específica del registro de peso, solo el valor actual.
                return f'Su peso actual en el perfil es: {peso_kg:.1f} kg'
            else:
                return 'No hay peso registrado en su perfil.'
        except Exception as e:
            print(f"Error al obtener peso desde la API: {e}")
            return 'Error al cargar peso desde el servidor.'
    
    def get_fecha(self) -> str | None:
        """
        Obtiene la fecha del último peso registrado.
        NOTA: La API actual no almacena un historial de pesos con fechas.
        Esta función podría retornar la fecha de última modificación del perfil si la API la proveyera.
        Por ahora, retorna None.
        """
        # user_data = self.api_client.get_user_profile()
        # if user_data and 'fecha_actualizacion_perfil' in user_data:
        #    return user_data['fecha_actualizacion_perfil']
        print("INFO: get_fecha no puede obtener fecha específica del peso con la API actual.")
        return None

# Ejemplo de uso para testing
if __name__ == "__main__":
    # Para probar este diálogo, necesitaríamos un mock de api_client.
    # Ejemplo de Mock APIClient:
    class MockAPIClient:
        def __init__(self):
            self.profile = {'peso': 75.5, 'altura': 180, 'sexo': 'Masculino', 'edad': 30}

        def get_user_profile(self):
            print("MockAPIClient: get_user_profile() llamado")
            # Simular un error ocasional:
            # import random
            # if random.random() < 0.1:
            #     raise Exception("Error simulado de red al obtener perfil")
            return self.profile

        def update_user_profile(self, data):
            print(f"MockAPIClient: update_user_profile() llamado con data: {data}")
            if 'peso' in data:
                # Simular un error si el peso es > 300 (ejemplo de validación de API)
                # if data['peso'] > 300:
                #     raise Exception(f"Error de API: Peso {data['peso']} excede el límite.")
                self.profile['peso'] = data['peso']
                print(f"MockAPIClient: Peso actualizado a {self.profile['peso']}")
            # Simular error si el endpoint no existiera (ej. lanzando un error específico)
            # raise requests.exceptions.HTTPError(response=type('Response', (), {'status_code': 404, 'reason': 'Not Found'}))


    from PyQt6.QtWidgets import QApplication
    import sys
    import os
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Aplicar tema oscuro
    app.setStyleSheet("""
        QWidget {
            background-color: #2C3E50;
            color: white;
        }
    """)
    
    # Crear estructura de carpetas de prueba si no existe
    test_user = "test_user"
    if not os.path.exists(f"./users/{test_user}"):
        os.makedirs(f"./users/{test_user}", exist_ok=True)
    
    def test_callback():
        print("Peso actualizado - callback ejecutado")
    
    dialog = Peso(usuario=test_user, callback=test_callback)
    dialog.exec()
    
    sys.exit(app.exec())