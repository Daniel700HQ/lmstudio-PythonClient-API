# chat_display.py
# Componente de la UI que muestra la conversación del chat.

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

# Importación local del visor de imágenes
from image_viewer import ImageViewer

class ClickableImageLabel(QLabel):
    """Un QLabel que emite una señal 'clicked' cuando se hace clic en él."""
    # La señal no necesita pasar datos, ya que los gestionaremos en la conexión.
    clicked = pyqtSignal()

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setCursor(Qt.PointingHandCursor) # Cambia el cursor para indicar que es clickeable

    def mousePressEvent(self, event):
        self.clicked.emit()

class ChatDisplay(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignTop)

    def add_message(self, role, content, image_path=None):
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(5, 5, 5, 5)

        role_label = QLabel(f"<b>{role.capitalize()}:</b>")
        message_layout.addWidget(role_label)

        if image_path:
            # 1. Se crea el QPixmap con la imagen original a resolución completa.
            #    Esta es la variable que queremos mostrar en pantalla completa.
            original_pixmap = QPixmap(image_path)
            
            if not original_pixmap.isNull():
                # 2. Se crea una versión escalada (miniatura) solo para mostrarla en el chat.
                thumbnail_pixmap = original_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label = ClickableImageLabel(thumbnail_pixmap)
                
                # 3. Se conecta la señal 'clicked' del label. Usamos una lambda para asegurarnos
                #    de que se llama a 'show_full_screen_image' con el pixmap ORIGINAL, no la miniatura.
                image_label.clicked.connect(lambda pix=original_pixmap: self.show_full_screen_image(pix))
                
                message_layout.addWidget(image_label)

        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            message_layout.addWidget(content_label)

        # Estilo diferencial para usuario y asistente
        style = "border-radius: 5px; margin-bottom: 5px; padding: 8px;"
        if role == "user":
            message_widget.setStyleSheet(f"background-color: #2E3440; {style}")
        else:
            message_widget.setStyleSheet(f"background-color: #4C566A; {style}")

        self.layout.addWidget(message_widget)
        
        # Auto-scroll hacia el final para ver el último mensaje
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def show_full_screen_image(self, pixmap_to_show):
        """
        Esta función recibe el QPixmap que debe mostrar y lo pasa al visor.
        Gracias a la lambda, siempre será el pixmap original.
        """
        viewer = ImageViewer(pixmap_to_show, self)
        viewer.exec_()

    def clear_chat(self):
        """Limpia todos los widgets del layout de forma segura."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()