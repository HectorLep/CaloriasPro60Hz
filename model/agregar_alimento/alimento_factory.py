from abc import ABC, abstractmethod
from .repositorio_alimentos import SqliteAlimentoRepository
from .servicio_alimentos import AlimentoService, PyQt6NotificationService

# Interfaz para la fábrica
class AlimentoFactory(ABC):
    @abstractmethod
    def crear_alimento_service(self, usuario: str) -> AlimentoService:
        pass

    @abstractmethod
    def crear_notification_service(self, parent=None) -> PyQt6NotificationService:
        pass

# Fábrica concreta para SQLite
class SqliteAlimentoFactory(AlimentoFactory):
    def crear_alimento_service(self, usuario: str) -> AlimentoService:
        db_path = f"./users/{usuario}/alimentos.db"
        repository = SqliteAlimentoRepository(db_path)
        return AlimentoService(repository)

    def crear_notification_service(self, parent=None) -> PyQt6NotificationService:
        return PyQt6NotificationService(parent)