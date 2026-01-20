"""
Módulo da Janela Principal (MainWindow).

Interface principal do sistema financeiro com design moderno
incluindo header, sidebar e cards financeiros dinâmicos.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import date, timedelta

from interface.styles import DIALOG_STYLES
from interface.dialogs.add import (
    NovaReceitaDialog, NovaDespesaDialog, NovaNotaServicoDialog
)
from interface.dialogs.reports import (
    RelatorioReceitasDialog, RelatorioDespesasDialog, 
    RelatorioNotasDialog, RelatorioGeralDialog
)
from interface.pages.employees_page import EmployeesPage


class MainWindow(QMainWindow):
    def __init__(self, sistema):
        super().__init__()

        self.sistema = sistema
        self.setWindowTitle("Sistema Financeiro - Torneadora")
        self.resize(1100, 750)
        
        self.janela_funcionarios = None
        
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface principal."""
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: #F5F5F5;")
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header azul escuro
        self._create_header(main_layout)
        
        # Container principal (sidebar + conteúdo)
        content_container = QHBoxLayout()
        content_container.setContentsMargins(0, 0, 0, 0)
        content_container.setSpacing(0)
        
        # Sidebar
        self._create_sidebar(content_container)
        
        # Área de conteúdo
        self._create_content_area(content_container)
        
        main_layout.addLayout(content_container, 1)

    def _create_header(self, parent_layout):
        """Cria o header azul escuro."""
        header = QFrame()
        header.setFixedHeight(55)
        header.setStyleSheet("background-color: #2B4B7C;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(12)
        
        # Logo
        logo = QLabel("🔧")
        logo.setStyleSheet("""
            font-size: 24px;
            background-color: #3D5A80;
            padding: 6px 10px;
            border-radius: 8px;
        """)
        header_layout.addWidget(logo)
        
        # Menu
        menu_btn = self._header_icon("☰")
        header_layout.addWidget(menu_btn)
        
        # Ajuda
        help_btn = self._header_icon("?")
        help_btn.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            background: transparent;
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 15px;
            padding: 4px 10px;
        """)
        header_layout.addWidget(help_btn)
        
        # Notificações
        notif_btn = self._header_icon("🔔")
        header_layout.addWidget(notif_btn)
        
        header_layout.addStretch()
        parent_layout.addWidget(header)

    def _header_icon(self, icon):
        """Cria um ícone do header."""
        btn = QPushButton(icon)
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                color: white;
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
                border-radius: 6px;
            }
        """)
        return btn

    def _create_sidebar(self, parent_layout):
        """Cria a sidebar de navegação."""
        sidebar = QFrame()
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #E8E8E8;
                border-right: 1px solid #D0D0D0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(5)
        
        # Itens do menu - APENAS FUNCIONAIS
        menu_items = [
            ("👥", "Funcionários", self.abrir_funcionarios),
            ("📊", "Relatórios", self.abrir_relatorio_geral),
            ("📋", "Receitas", self.abrir_relatorio_receitas),
            ("📋", "Despesas", self.abrir_relatorio_despesas),
            ("📋", "Notas", self.abrir_relatorio_notas),
        ]
        
        for icon, text, callback in menu_items:
            btn = self._create_sidebar_item(icon, text, callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        parent_layout.addWidget(sidebar)

    def _create_sidebar_item(self, icon, text, callback):
        """Cria um item da sidebar."""
        btn = QPushButton(f"{icon}  {text}")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-size: 14px;
                color: #4A4A4A;
                background: transparent;
                border: none;
                border-left: 3px solid transparent;
            }
            QPushButton:hover {
                background-color: #D8D8D8;
                border-left: 3px solid #2B4B7C;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def _create_content_area(self, parent_layout):
        """Cria a área principal de conteúdo."""
        content = QFrame()
        content.setStyleSheet("background-color: #F5F5F5;")
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(20)
        
        # Título
        title = QLabel("Financeiro")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #333;")
        content_layout.addWidget(title)
        
        # ===== SEÇÃO: RESUMO FINANCEIRO =====
        self._create_financial_section(content_layout)
        
        # ===== SEÇÃO: NOTAS DE SERVIÇO =====
        self._create_notes_section(content_layout)
        
        # ===== SEÇÃO: INFORMAÇÕES ADICIONAIS =====
        self._create_info_section(content_layout)
        
        content_layout.addStretch()
        parent_layout.addWidget(content, 1)

    def _create_financial_section(self, parent_layout):
        """Cria a seção de resumo financeiro."""
        # Container com fundo branco
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 20, 25, 20)
        container_layout.setSpacing(15)
        
        # Cards financeiros
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        
        # Obter dados
        total_receitas = self._calcular_total_receitas()
        total_despesas = self._calcular_total_despesas()
        resultado = total_receitas - total_despesas
        
        # Card Receitas
        self.card_receitas = self._create_financial_card(
            self._formatar_moeda(total_receitas),
            "Total em receitas",
            "#00b33c"
        )
        cards_layout.addWidget(self.card_receitas)
        
        # Card Despesas
        self.card_despesas = self._create_financial_card(
            self._formatar_moeda(total_despesas),
            "Total em despesas",
            "#E53935"
        )
        cards_layout.addWidget(self.card_despesas)
        
        # Card Resultado
        cor_resultado = "#2196F3" if resultado >= 0 else "#E53935"
        self.card_resultado = self._create_financial_card(
            self._formatar_moeda(resultado),
            "Resultado",
            cor_resultado
        )
        cards_layout.addWidget(self.card_resultado)
        
        cards_layout.addStretch()
        container_layout.addLayout(cards_layout)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        btn_receita = self._create_action_button("+ Receita", "#00b33c", self.abrir_dialogo_receita)
        buttons_layout.addWidget(btn_receita)
        
        btn_despesa = self._create_action_button("+ Despesa", "#E53935", self.abrir_dialogo_despesa)
        buttons_layout.addWidget(btn_despesa)
        
        buttons_layout.addStretch()
        container_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(container)

    def _create_financial_card(self, valor, titulo, cor):
        """Cria um card de resumo financeiro."""
        card = QFrame()
        card.setFixedWidth(180)
        card.setStyleSheet("background: transparent; border: none;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Valor
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {cor};")
        layout.addWidget(lbl_valor)
        
        # Título
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(lbl_titulo)
        
        # Barra colorida
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background-color: {cor}; border-radius: 2px;")
        layout.addWidget(bar)
        
        # Guardar referência
        card.valor_label = lbl_valor
        
        return card

    def _create_action_button(self, texto, cor, callback):
        """Cria um botão de ação colorido."""
        btn = QPushButton(texto)
        btn.setFixedHeight(40)
        btn.setFixedWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor};
                color: white;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(cor)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def _create_notes_section(self, parent_layout):
        """Cria a seção de notas de serviço."""
        container = QFrame()
        container.setFixedWidth(380)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("Notas de serviço")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Resumo de notas
        pendentes = self._contar_ordens_pendentes()
        total_ordens = self._contar_total_ordens()
        
        info_layout = QHBoxLayout()
        
        lbl_pendentes = QLabel(f"📌 {pendentes} pendentes")
        lbl_pendentes.setStyleSheet("font-size: 13px; color: #E53935;")
        info_layout.addWidget(lbl_pendentes)
        
        lbl_total = QLabel(f"📋 {total_ordens} total")
        lbl_total.setStyleSheet("font-size: 13px; color: #666;")
        info_layout.addWidget(lbl_total)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Guardar referências
        self.lbl_pendentes = lbl_pendentes
        self.lbl_total_ordens = lbl_total
        
        # Botão nova nota
        btn_nova = QPushButton("  +   Nova nota de serviço")
        btn_nova.setFixedHeight(40)
        btn_nova.setCursor(Qt.PointingHandCursor)
        btn_nova.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #555;
                border: 1px solid #D0D0D0;
                border-radius: 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
        """)
        btn_nova.clicked.connect(self.abrir_dialogo_nota_servico)
        layout.addWidget(btn_nova)
        
        parent_layout.addWidget(container)

    def _create_info_section(self, parent_layout):
        """Cria seção com informações adicionais."""
        # Container horizontal para dois cards
        row = QHBoxLayout()
        row.setSpacing(20)
        
        # Card: Funcionários
        card_func = self._create_info_card(
            "👥 Funcionários",
            self._contar_funcionarios(),
            "cadastrados",
            self.abrir_funcionarios
        )
        row.addWidget(card_func)
        
        # Card: Receitas do mês
        receitas_mes = self._calcular_receitas_mes()
        card_rec_mes = self._create_info_card(
            "📈 Este mês",
            self._formatar_moeda(receitas_mes),
            "em receitas",
            lambda: self.abrir_relatorio_receitas(filtro_inicial="Mês")
        )
        row.addWidget(card_rec_mes)
        
        # Card: Despesas do mês
        despesas_mes = self._calcular_despesas_mes()
        card_desp_mes = self._create_info_card(
            "📉 Este mês",
            self._formatar_moeda(despesas_mes),
            "em despesas",
            lambda: self.abrir_relatorio_despesas(filtro_inicial="Mês")
        )
        row.addWidget(card_desp_mes)
        
        row.addStretch()
        parent_layout.addLayout(row)

    def _create_info_card(self, titulo, valor, subtitulo, callback):
        """Cria um card informativo clicável."""
        card = QPushButton()
        card.setFixedSize(180, 100)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #FAFAFA;
                border-color: #2B4B7C;
            }
        """)
        card.clicked.connect(callback)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(lbl_titulo)
        
        lbl_valor = QLabel(str(valor))
        lbl_valor.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(lbl_valor)
        
        lbl_sub = QLabel(subtitulo)
        lbl_sub.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(lbl_sub)
        
        layout.addStretch()
        
        return card

    # ========= MÉTODOS DE CÁLCULO =========

    def _calcular_total_receitas(self):
        try:
            return sum(r.valor for r in self.sistema.listar_recebimentos())
        except:
            return 0.0

    def _calcular_total_despesas(self):
        try:
            return sum(d.valor for d in self.sistema.listar_despesas())
        except:
            return 0.0

    def _contar_ordens_pendentes(self):
        try:
            return len([o for o in self.sistema.listar_ordens_servico() if not o.foi_pago])
        except:
            return 0

    def _contar_total_ordens(self):
        try:
            return len(self.sistema.listar_ordens_servico())
        except:
            return 0

    def _contar_funcionarios(self):
        try:
            return len(self.sistema.listar_funcionarios())
        except:
            return 0

    def _calcular_receitas_mes(self):
        try:
            hoje = date.today()
            receitas = self.sistema.listar_recebimentos()
            return sum(r.valor for r in receitas if r.data.year == hoje.year and r.data.month == hoje.month)
        except:
            return 0.0

    def _calcular_despesas_mes(self):
        try:
            hoje = date.today()
            despesas = self.sistema.listar_despesas()
            return sum(d.valor for d in despesas if d.data.year == hoje.year and d.data.month == hoje.month)
        except:
            return 0.0

    def _formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _darken_color(self, hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = max(0, int(r * 0.85))
        g = max(0, int(g * 0.85))
        b = max(0, int(b * 0.85))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _atualizar_resumo(self):
        """Atualiza todos os valores dinâmicos."""
        total_receitas = self._calcular_total_receitas()
        total_despesas = self._calcular_total_despesas()
        resultado = total_receitas - total_despesas
        
        self.card_receitas.valor_label.setText(self._formatar_moeda(total_receitas))
        self.card_despesas.valor_label.setText(self._formatar_moeda(total_despesas))
        self.card_resultado.valor_label.setText(self._formatar_moeda(resultado))
        
        cor_resultado = "#2196F3" if resultado >= 0 else "#E53935"
        self.card_resultado.valor_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {cor_resultado};")
        
        self.lbl_pendentes.setText(f"📌 {self._contar_ordens_pendentes()} pendentes")
        self.lbl_total_ordens.setText(f"📋 {self._contar_total_ordens()} total")

    # ========= AÇÕES =========

    def abrir_dialogo_receita(self):
        if NovaReceitaDialog(self.sistema, self).exec():
            self._atualizar_resumo()

    def abrir_dialogo_despesa(self):
        if NovaDespesaDialog(self.sistema, self).exec():
            self._atualizar_resumo()

    def abrir_dialogo_nota_servico(self):
        if NovaNotaServicoDialog(self.sistema, self).exec():
            self._atualizar_resumo()
    
    def abrir_funcionarios(self):
        if self.janela_funcionarios is None:
            self.janela_funcionarios = EmployeesPage(self.sistema)
            self.janela_funcionarios.setWindowTitle("Gestão de Funcionários")
            self.janela_funcionarios.resize(900, 650)
        self.janela_funcionarios.show()
        self.janela_funcionarios.raise_()
        self.janela_funcionarios.activateWindow()

    def abrir_relatorio_receitas(self, filtro_inicial=None):
        RelatorioReceitasDialog(self.sistema, self, filtro_inicial=filtro_inicial).exec()
        self._atualizar_resumo()

    def abrir_relatorio_despesas(self, filtro_inicial=None):
        RelatorioDespesasDialog(self.sistema, self, filtro_inicial=filtro_inicial).exec()
        self._atualizar_resumo()

    def abrir_relatorio_notas(self):
        RelatorioNotasDialog(self.sistema, self).exec()
        self._atualizar_resumo()

    def abrir_relatorio_geral(self, filtro_inicial=None):
        RelatorioGeralDialog(self.sistema, self, filtro_inicial=filtro_inicial).exec()
        self._atualizar_resumo()
