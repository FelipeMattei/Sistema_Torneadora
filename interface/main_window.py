"""
Módulo da Janela Principal (MainWindow).

Contém a classe MainWindow que serve como o hub central da aplicação,
permitindo acesso aos diálogos de cadastro e de relatório.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt

# Importa os diálogos do subpacote .dialogs
from interface.dialogs.add import (
    NovaReceitaDialog, NovaDespesaDialog, NovaNotaServicoDialog
)
from interface.dialogs.reports import (
    RelatorioReceitasDialog, RelatorioDespesasDialog, 
    RelatorioNotasDialog, RelatorioGeralDialog
)

class MainWindow(QMainWindow):
    def __init__(self, sistema):
        super().__init__()

        self.sistema = sistema
        self.setWindowTitle("Financeiro - Torneadora")
        self.resize(1000, 650)
        
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Título
        lbl_titulo = QLabel("Sistema Financeiro & Serviços")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(lbl_titulo)

        # --- SEÇÃO CADASTROS ---
        lbl_cad = QLabel("Cadastros Rápidos")
        lbl_cad.setStyleSheet("font-size: 16px; font-weight: 600; color: #555; margin-top: 20px;")
        layout.addWidget(lbl_cad)

        bar_cad = QHBoxLayout()
        bar_cad.setSpacing(12)
        
        btn_rec = self._make_btn("+ Receita", self.abrir_dialogo_receita, "#00b33c")
        btn_desp = self._make_btn("+ Despesa", self.abrir_dialogo_despesa, "#bd2c00")
        btn_nota = self._make_btn("+ Nota de serviço", self.abrir_dialogo_nota_servico, "#0066cc")
        
        bar_cad.addWidget(btn_rec)
        bar_cad.addWidget(btn_desp)
        bar_cad.addWidget(btn_nota)
        bar_cad.addStretch()
        layout.addLayout(bar_cad)

        # Divisor
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # --- SEÇÃO RELATÓRIOS ---
        lbl_rel = QLabel("Relatórios")
        lbl_rel.setStyleSheet("font-size: 18px; font-weight: 700; color: #333;")
        layout.addWidget(lbl_rel)

        bar_rel = QHBoxLayout()
        bar_rel.setSpacing(12)
        
        bar_rel.addWidget(self._make_btn("Receitas", self.abrir_relatorio_receitas))
        bar_rel.addWidget(self._make_btn("Despesas", self.abrir_relatorio_despesas))
        bar_rel.addWidget(self._make_btn("Notas de Serviço", self.abrir_relatorio_notas))
        bar_rel.addWidget(self._make_btn("Relatório Geral", self.abrir_relatorio_geral))
        bar_rel.addStretch()
        
        layout.addLayout(bar_rel)
        layout.addStretch()

    def _make_btn(self, texto, callback, cor_bg=None):
        """Helper para criar botões padronizados."""
        btn = QPushButton(texto)
        btn.setFixedHeight(40)
        btn.clicked.connect(callback)
        # Estilo simples direto aqui ou no arquivo QSS
        style = "font-weight: 600; padding: 0 15px; border-radius: 6px;"
        if cor_bg:
            style += f" background-color: {cor_bg}; color: white;"
        else:
            style += " background-color: #f0f0f0; border: 1px solid #ccc;"
        btn.setStyleSheet(style)
        return btn

    # --- AÇÕES ---

    def abrir_dialogo_receita(self):
        NovaReceitaDialog(self.sistema, self).exec()

    def abrir_dialogo_despesa(self):
        NovaDespesaDialog(self.sistema, self).exec()

    def abrir_dialogo_nota_servico(self):
        NovaNotaServicoDialog(self.sistema, self).exec()

    def abrir_relatorio_receitas(self):
        RelatorioReceitasDialog(self.sistema, self).exec()

    def abrir_relatorio_despesas(self):
        RelatorioDespesasDialog(self.sistema, self).exec()

    def abrir_relatorio_notas(self):
        RelatorioNotasDialog(self.sistema, self).exec()

    def abrir_relatorio_geral(self):
        RelatorioGeralDialog(self.sistema, self).exec()
