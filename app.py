"""
Ponto de entrada da aplicação financeira.

Este módulo inicializa:
- o banco de dados (Database)
- a camada de serviços (SistemaFinanceiro)
- a interface gráfica (MainWindow, em interface.py)
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from database import Database
from services import SistemaFinanceiro
from interface import MainWindow


def main():
    # High DPI para texto mais suave
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # ===== Fonte global: Segoe UI =====
    base_font = QFont("Segoe UI")
    base_font.setPointSize(10)   # se quiser maior, teste 10.5 ou 11
    app.setFont(base_font)
    # ==================================

    # Banco e regras de negócio
    db = Database("financeiro.db")
    sistema = SistemaFinanceiro(db)

    # Interface principal
    window = MainWindow(sistema)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
