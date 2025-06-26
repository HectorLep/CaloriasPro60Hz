# auth_service.py (Versión corregida y completa)

from abc import ABC, abstractmethod
import requests

class IAuthService(ABC):
    @abstractmethod
    def verificar_credenciales(self, usuario, contrasena):
        pass
    
    @abstractmethod
    def registrar_usuario(self, datos_usuario):
        pass
    
    @abstractmethod
    def obtener_usuarios(self):
        pass
    
    @abstractmethod
    def guardar_usuario_actual(self, usuario):
        pass
    
    @abstractmethod
    def limpiar_usuario_actual(self):
        pass

    @abstractmethod
    def obtener_usuario_actual(self):
        pass

class AuthService(IAuthService):
    def __init__(self, api_base_url="http://127.0.0.1:8000"):
        self.api_base_url = api_base_url
        self.current_user = None
        self.access_token = None
    
    def verificar_credenciales(self, nombre_usuario, contraseña):
        """
        Inicia sesión usando la API y verifica las credenciales.
        Este método ya estaba funcionando correctamente.
        """
        try:
            login_data = {'username': nombre_usuario, 'password': contraseña}
            response = requests.post(
                f"{self.api_base_url}/login/",
                data=login_data # OAuth2PasswordRequestForm espera 'data' (form-data)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.guardar_usuario_actual(nombre_usuario) # Guardamos el usuario en la sesión
                return True
            else:
                print(f"Error de credenciales: {response.json().get('detail')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al iniciar sesión: {e}")
            return False

    def obtener_usuarios(self):
        """
        Obtiene la lista de nombres de usuario desde el endpoint /users/ de la API.
        """
        try:
            response = requests.get(f"{self.api_base_url}/users/")
            response.raise_for_status()  # Lanza una excepción si hay un error HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API para obtener usuarios: {e}")
            return [] # Devuelve lista vacía en caso de error

    def registrar_usuario(self, datos_usuario):
        """
        Registra un usuario en la API.
        Este método ya estaba funcionando correctamente.
        """
        try:
            registro_data = {
                "nombre_usuario": datos_usuario['nombre'],
                "password": datos_usuario['contra'],
                "sexo": datos_usuario['sexo'],
                "peso": float(datos_usuario['peso']),
                "altura": int(datos_usuario['altura']),
                "meta_calorias": int(datos_usuario['meta_calorias']),
                "nivel_actividad": datos_usuario['nivel_actividad'],
                "fecha_nacimiento": datos_usuario['fecha_nacimiento'].isoformat(),
                "edad": int(datos_usuario['edad'])
            }
            response = requests.post(f"{self.api_base_url}/register/", json=registro_data)
            
            if response.status_code == 201:
                return True
            else:
                print(f"Error al registrar: {response.json().get('detail')}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al registrar: {e}")
            return False

    def guardar_usuario_actual(self, usuario):
        self.current_user = usuario
        return True

    def limpiar_usuario_actual(self):
        self.current_user = None
        self.access_token = None

    def obtener_usuario_actual(self):
        return self.current_user