import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.database.connection import Database
from app.services.finance_service import SistemaFinanceiro
from app.ui.main_window import MainWindow


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

    print("Starting app...")
    # Banco e regras de negócio
    # Caminho do banco: ajustável via config ou hardcoded por enquanto
    print("Initializing Database...")
    db = Database("financeiro.db")
    print("Initializing Service...")
    sistema = SistemaFinanceiro(db)

    # Interface principal
    print("Initializing MainWindow...")
    window = MainWindow(sistema)
    print("Showing MainWindow...")
    window.show()

    print("Entering Event Loop...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
