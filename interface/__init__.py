"""
Pacote Interface.

Este pacote contém toda a lógica de interface gráfica (GUI) da aplicação.
Foi refatorado para dividir responsabilidades em módulos menores:
- styles.py: Definições de CSS/QSS
- helpers.py: Funções utilitárias
- main_window.py: Janela principal
- dialogs/: Subpacote com todos os diálogos do sistema.
"""

from interface.main_window import MainWindow

__all__ = ["MainWindow"]
