"""
Página de Gestão de Funcionários.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon

from interface.dialogs.add_edit_employee import AddEditEmployeeDialog
from models import Funcionario

class EmployeeCard(QFrame):
    """Card representando um funcionário na lista."""
    clicked = Signal(Funcionario)

    def __init__(self, funcionario: Funcionario, parent=None):
        super().__init__(parent)
        self.funcionario = funcionario
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            EmployeeCard {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            EmployeeCard:hover {
                border: 1px solid #aaa;
                background-color: #f9f9f9;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Foto (Thumbnail)
        lbl_foto = QLabel()
        lbl_foto.setFixedSize(70, 70)
        # O stylesheet border-radius ajuda no bg, mas para a imagem precisamos arredondar o pixmap manualmente
        lbl_foto.setStyleSheet("background-color: #eee; border-radius: 35px; border: 1px solid #ccc;")
        lbl_foto.setAlignment(Qt.AlignCenter)
        
        if funcionario.foto_caminho:
            pix = QPixmap(funcionario.foto_caminho)
            if not pix.isNull():
                # Criar pixmap circular manualmente
                size = 70
                rounded = QPixmap(size, size)
                rounded.fill(Qt.transparent)
                
                # Escalar imagem mantendo aspect ratio para cobrir o quadrado (crop center)
                scaled_pix = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                
                # Recortar centro
                x = (scaled_pix.width() - size) // 2
                y = (scaled_pix.height() - size) // 2
                cropped = scaled_pix.copy(x, y, size, size)
                
                # Pintar no pixmap transparente com pincel circular
                from PySide6.QtGui import QPainter, QBrush, QPainterPath
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                
                painter.drawPixmap(0, 0, cropped)
                painter.end()
                
                lbl_foto.setPixmap(rounded)
        else:
             lbl_foto.setText(funcionario.nome[0].upper())
             lbl_foto.setStyleSheet("border-radius: 35px; background-color: #ddd; font-size: 24px; font-weight: bold; color: #555;")
        
        layout.addWidget(lbl_foto)
        
        # Infos
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        lbl_nome = QLabel(funcionario.nome)
        lbl_nome.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; border: none; background: transparent;")
        
        lbl_cargo = QLabel(f"{funcionario.cargo} • {funcionario.telefone}")
        lbl_cargo.setStyleSheet("font-size: 14px; color: #666; border: none; background: transparent;")
        
        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_cargo)
        
        layout.addLayout(info_layout)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.funcionario)
        super().mousePressEvent(event)


class EmployeesPage(QWidget):
    """Página principal de funcionários."""
    
    voltar_signal = Signal() # Sinal para voltar ao menu principal se necessario

    def __init__(self, sistema, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self._setup_ui()
        self.carregar_funcionarios()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        
        lbl_titulo = QLabel("Funcionários")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        
        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Buscar por nome...")
        self.txt_busca.setFixedWidth(300)
        self.txt_busca.setStyleSheet("background-color: #ffffff;border-radius: 10px;border: 1px solid #d0d0d0;padding: 8px 12px;selection-background-color: #00b33c;selection-color: #ffffff; width: 40px;")
        self.txt_busca.textChanged.connect(self._filtrar)
        
        btn_novo = QPushButton("+ Novo Funcionário")
        btn_novo.setObjectName("primaryButton")
        btn_novo.setStyleSheet("background-color: #00b33c;color: white;border-radius: 10px;padding: 10px 25px;border: 1px solid #9F9F9F;font-weight: 600;")
        btn_novo.clicked.connect(self._novo_funcionario)
        
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.txt_busca)
        header_layout.addWidget(btn_novo)
        
        layout.addLayout(header_layout)
        
        # Lista Scrollavel
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        self.container_lista = QWidget()
        self.layout_lista = QVBoxLayout(self.container_lista)
        self.layout_lista.setAlignment(Qt.AlignTop)
        self.layout_lista.setSpacing(10)
        
        self.scroll_area.setWidget(self.container_lista)
        layout.addWidget(self.scroll_area)
        
        self.funcionarios_cache = []

    def carregar_funcionarios(self):
        # Limpar
        while self.layout_lista.count():
            child = self.layout_lista.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        funcionarios = self.sistema.listar_funcionarios()
        self.funcionarios_cache = funcionarios
        
        self._popular_lista(funcionarios)

    def _popular_lista(self, funcionarios):
        # Limpar visual apenas
        while self.layout_lista.count():
            child = self.layout_lista.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not funcionarios:
            lbl_vazio = QLabel("Nenhum funcionário encontrado.")
            lbl_vazio.setStyleSheet("color: #777; font-size: 16px; margin-top: 20px;")
            lbl_vazio.setAlignment(Qt.AlignCenter)
            self.layout_lista.addWidget(lbl_vazio)
            return

        for f in funcionarios:
            card = EmployeeCard(f)
            card.clicked.connect(self._editar_funcionario)
            self.layout_lista.addWidget(card)

    def _filtrar(self, texto):
        texto = texto.lower()
        filtrados = [f for f in self.funcionarios_cache if texto in f.nome.lower()]
        self._popular_lista(filtrados)

    def _novo_funcionario(self):
        diag = AddEditEmployeeDialog(self.sistema, self)
        if diag.exec():
            self.carregar_funcionarios()

    def _editar_funcionario(self, funcionario):
        diag = AddEditEmployeeDialog(self.sistema, self, funcionario=funcionario)
        if diag.exec():
            self.carregar_funcionarios()
