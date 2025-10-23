# app.py
# Punto de entrada para ejecutar la aplicación.

# pip install PyQt5 requests

import sys
from PyQt5.QtWidgets import QApplication

# Importación de la ventana principal desde el módulo gui
from gui import ChatGUI

def main():
    """Punto de entrada principal de la aplicación."""
    app = QApplication(sys.argv)
    main_window = ChatGUI()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()