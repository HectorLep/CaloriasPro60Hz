from PyQt6.QtCore import QRect


class BuscadorManager:
    def __init__(self, parent, entry, listbox, repository):
        self.entry_buscar = entry
        self.coincidencias = listbox
        self.repository = repository
        self.parent = parent
        self.alimentos_buscar = []
        self.match = []
        
        # Conectar eventos
        self.entry_buscar.textChanged.connect(self.obtener_busqueda)
        self.coincidencias.itemClicked.connect(self.on_item_clicked)

    def obtener_busqueda(self):
        typeado = self.entry_buscar.text()
        if not typeado or typeado == '':
            self.alimentos_buscar = []
            self.match = []
            self.update_coincidencias()

            # 🔥 Ocultar controles si se borra el texto
            if hasattr(self.parent, '_hide_alimento_controls'):
                self.parent._hide_alimento_controls()
            return

        self.alimentos_buscar = self.repository.cargar_alimentos()
        self.match = [i for i in self.alimentos_buscar if typeado.lower() in i.lower()]
        self.update_coincidencias()


    def update_coincidencias(self):
        self.coincidencias.clear()
        num_coincidencias = len(self.match)

        if num_coincidencias > 0:
            height = min(num_coincidencias, 5)

            # Posicionar justo debajo del entry_buscar
            x = self.entry_buscar.x()
            y = self.entry_buscar.y() + self.entry_buscar.height()
            width = self.entry_buscar.width()
            item_height = 35  # altura por ítem aprox.
            list_height = item_height * height

            self.coincidencias.setGeometry(QRect(x, y, width, list_height))
            self.coincidencias.raise_()  # Asegurar que esté al frente
            self.coincidencias.show()

            for alimento in self.match:
                self.coincidencias.addItem(alimento)
        else:
            self.coincidencias.hide()

    def on_item_clicked(self, item):
        """Maneja el click en un elemento de la lista"""
        self.rellenar_con_texto(item.text())

    def rellenar_con_texto(self, texto):
        """Rellena el entry con el texto seleccionado y activa los controles"""
        self.entry_buscar.setText(texto)
        self.coincidencias.hide()

        if hasattr(self.parent, 'on_alimento_select'):
            self.parent.on_alimento_select(texto)

    def rellenar(self, callback):
        """Método para compatibilidad con el callback original"""
        current_item = self.coincidencias.currentItem()
        if current_item:
            alimento_seleccionado = current_item.text()
            self.entry_buscar.clear()
            self.entry_buscar.setText(alimento_seleccionado)
            self.coincidencias.hide()
            callback(alimento_seleccionado)
