"""
Módulo de Relatórios (Reports).

Contém os diálogos de visualização de dados em tabelas:
- RelatorioReceitasDialog
- RelatorioDespesasDialog
- RelatorioNotasDialog
- RelatorioGeralDialog
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import date

from interface.styles import DIALOG_STYLES  
from interface.helpers import _date_to_str
from interface.dialogs.details import DetalheLancamentoDialog
from interface.date_filter_widget import DateFilterWidget
from excel_generator import gerar_excel_relatorio

# ===================== BASE RELATÓRIO =====================

class BaseRelatorioDialog(QDialog):
    """Classe base para evitar repetição de setup de UI (Header, Tabela, Footer)."""
    
    def __init__(self, sistema, titulo, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self._linhas_raw = []
        
        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(950, 560)
        self.setStyleSheet(DIALOG_STYLES)
        
        self._setup_base_ui(titulo)

    def _setup_base_ui(self, titulo):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame(objectName="card")
        self.layout_card = QVBoxLayout(self.card)
        self.layout_card.setContentsMargins(32,24,32,24)
        self.layout_card.setSpacing(16)
        
        # Header
        h = QHBoxLayout()
        h.addWidget(QLabel(titulo, objectName="title"))
        h.addStretch()
        btn_close = QPushButton("✕", objectName="closeButton")
        btn_close.setFixedSize(40,40)
        btn_close.clicked.connect(self.close)
        h.addWidget(btn_close)
        self.layout_card.addLayout(h)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout_card.addWidget(line)
        
        root.addWidget(self.card)

    def _add_date_filter(self):
        """Adiciona o novo widget de filtro de data."""
        self.date_filter = DateFilterWidget()
        self.date_filter.filterChanged.connect(self.carregar_dados)
        return self.date_filter

    def _setup_tabela(self, colunas):
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.cellDoubleClicked.connect(self._abrir_detalhes_linha)
        self.layout_card.addWidget(self.tabela)

    def _abrir_detalhes_linha(self, row, col):
        if row < 0 or row >= len(self._linhas_raw): return
        info = self._linhas_raw[row]
        dlg = DetalheLancamentoDialog(info, self)
        dlg.exec()
        # Ao voltar, recarrega para refletir edições
        self.carregar_dados() 
        
    def carregar_dados(self):
        raise NotImplementedError
    
    def _gerar_pdf(self):
        """
        Método base para geração de PDF.
        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError


# ===================== RELATÓRIO RECEITAS =====================

class RelatorioReceitasDialog(BaseRelatorioDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(sistema, "Relatório de receitas", parent)
        
        # Filtro de data
        self.layout_card.addWidget(self._add_date_filter())
        self.btn_atualizar = QPushButton("Atualizar", objectName="secondaryButton")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        
        self._setup_tabela(["Data", "Valor", "Forma de pagamento"])
        
        # Footer
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total das receitas: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        
        # Botão para exportar Excel
        btn_excel = QPushButton("Exportar Excel", objectName="secondaryButton")
        btn_excel.clicked.connect(self._exportar_excel)
        footer.addWidget(btn_excel)
        
        footer.addWidget(self.btn_atualizar)
        self.layout_card.addLayout(footer)
        
        self.carregar_dados()

    def carregar_dados(self):
        # Obtém o range de datas do filtro
        data_inicio, data_fim = self.date_filter.get_date_range()
        
        self._linhas_raw = []
        linhas = []
        total = 0.0
        
        # Usa o novo método de filtragem por data
        recebimentos = self.sistema.listar_recebimentos_por_data(data_inicio, data_fim)
        
        for r in recebimentos:
            
            linhas.append((r.data, r.valor, r.forma_pagamento.value))
            total += r.valor
            
            self._linhas_raw.append({
                "tipo": "Receita",
                "id": r.id,
                "data": r.data,
                "descricao": f"Recebimento ({r.forma_pagamento.value})",
                "valor": r.valor,
                "situacao": None,
                "forma_pagamento": r.forma_pagamento.value,
                "comprovante": r.comprovante_caminho
            })
            
        self.tabela.setRowCount(len(linhas))
        for i, (d, v, f) in enumerate(linhas):
            self.tabela.setItem(i, 0, QTableWidgetItem(_date_to_str(d)))
            self.tabela.setItem(i, 1, QTableWidgetItem(f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
            self.tabela.setItem(i, 2, QTableWidgetItem(f))
            
        self.lbl_total.setText(f"Total das receitas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _exportar_excel(self):
        """Exporta Excel do relatório de receitas."""
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Excel", "relatorio_receitas.xlsx", "Excel Files (*.xlsx)"
        )
        if not caminho:
            return
        
        data_inicio, data_fim = self.date_filter.get_date_range()
        recebimentos = self.sistema.listar_recebimentos_por_data(data_inicio, data_fim)
        
        colunas = ["Data", "Valor", "Forma de Pagamento"]
        linhas = []
        total = 0.0
        
        for r in recebimentos:
            linhas.append((r.data, r.valor, r.forma_pagamento.value))
            total += r.valor
        
        modo = self.date_filter.get_modo_texto()
        periodo = "Todos os registros" if modo == "Tudo" else self.date_filter.lbl_info.text()
        saldo = f"Total das receitas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        sucesso = gerar_excel_relatorio(
            caminho, "Relatório de Receitas", periodo, saldo, colunas, linhas
        )
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Excel exportado com sucesso!\n{caminho}")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao exportar Excel.")


# ===================== RELATÓRIO DESPESAS =====================

class RelatorioDespesasDialog(BaseRelatorioDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(sistema, "Relatório de despesas", parent)
        
        self.layout_card.addWidget(self._add_date_filter())
        self.btn_atualizar = QPushButton("Atualizar", objectName="secondaryButton")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        
        self._setup_tabela(["Data", "Descrição", "Valor", "Forma pagamento", "A prazo?"])
        
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total das despesas: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        
        btn_excel = QPushButton("Exportar Excel", objectName="secondaryButton")
        btn_excel.clicked.connect(self._exportar_excel)
        footer.addWidget(btn_excel)
        
        footer.addWidget(self.btn_atualizar)
        self.layout_card.addLayout(footer)
        
        self.carregar_dados()

    def carregar_dados(self):
        data_inicio, data_fim = self.date_filter.get_date_range()
        
        self._linhas_raw = []
        linhas = []
        total = 0.0
        
        despesas = self.sistema.listar_despesas_por_data(data_inicio, data_fim)
        
        for d in despesas:
            
            prazo = "Sim" if d.eh_a_prazo else "Não"
            linhas.append((d.data, d.descricao, d.valor, d.forma_pagamento.value, prazo))
            total += d.valor
            
            self._linhas_raw.append({
                "tipo": "Despesa",
                "id": d.id,
                "data": d.data,
                "descricao": d.descricao,
                "valor": d.valor,
                "forma_pagamento": d.forma_pagamento.value,
                "eh_a_prazo": d.eh_a_prazo,
                "data_vencimento": d.data_vencimento,
                "situacao": None,
                "comprovante": d.comprovante_caminho
            })
            
        self.tabela.setRowCount(len(linhas))
        for i, (dt, desc, val, fp, prz) in enumerate(linhas):
            self.tabela.setItem(i, 0, QTableWidgetItem(_date_to_str(dt)))
            self.tabela.setItem(i, 1, QTableWidgetItem(desc))
            self.tabela.setItem(i, 2, QTableWidgetItem(f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
            self.tabela.setItem(i, 3, QTableWidgetItem(fp))
            self.tabela.setItem(i, 4, QTableWidgetItem(prz))
            
        self.lbl_total.setText(f"Total das despesas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _exportar_excel(self):
        """Exporta Excel do relatório de despesas."""
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Excel", "relatorio_despesas.xlsx", "Excel Files (*.xlsx)"
        )
        if not caminho:
            return
        
        data_inicio, data_fim = self.date_filter.get_date_range()
        despesas = self.sistema.listar_despesas_por_data(data_inicio, data_fim)
        
        colunas = ["Data", "Descrição", "Valor", "Forma Pagamento", "A prazo?"]
        linhas = []
        total = 0.0
        
        for d in despesas:
            prazo = "Sim" if d.eh_a_prazo else "Não"
            linhas.append((d.data, d.descricao, d.valor, d.forma_pagamento.value, prazo))
            total += d.valor
        
        modo = self.date_filter.get_modo_texto()
        periodo = "Todos os registros" if modo == "Tudo" else self.date_filter.lbl_info.text()
        saldo = f"Total das despesas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        sucesso = gerar_excel_relatorio(caminho, "Relatório de Despesas", periodo, saldo, colunas, linhas)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Excel exportado com sucesso!\n{caminho}")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao exportar Excel.")


# ===================== RELATÓRIO NOTAS =====================

class RelatorioNotasDialog(BaseRelatorioDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(sistema, "Relatório de notas de serviço", parent)
        
        self.layout_card.addWidget(self._add_date_filter())
        self.btn_atualizar = QPushButton("Atualizar", objectName="secondaryButton")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        
        self._setup_tabela(["Cliente", "Valor", "Pago", "Data"])
        
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        
        btn_excel = QPushButton("Exportar Excel", objectName="secondaryButton")
        btn_excel.clicked.connect(self._exportar_excel)
        footer.addWidget(btn_excel)
        
        footer.addWidget(self.btn_atualizar)
        self.layout_card.addLayout(footer)
        
        self.carregar_dados()

    def carregar_dados(self):
        data_inicio, data_fim = self.date_filter.get_date_range()
        
        self._linhas_raw = []
        linhas = []
        total = 0.0
        
        ordens = self.sistema.listar_ordens_servico_por_data(data_inicio, data_fim)
        
        for n in ordens:
            
            sit = "Paga" if n.foi_pago else "Não paga"
            linhas.append((n.cliente, n.valor_total, sit, n.data))
            total += n.valor_total
            
            fp = n.forma_pagamento.value if n.forma_pagamento else "Não definido"
            self._linhas_raw.append({
                "tipo": "Nota de serviço",
                "id": n.id,
                "data": n.data,
                "cliente": n.cliente,
                "descricao": n.descricao,
                "valor": n.valor_total,
                "situacao": sit,
                "pago_int": 1 if n.foi_pago else 0,
                "forma_pagamento": fp,
                "comprovante": None
            })
            
        self.tabela.setRowCount(len(linhas))
        for i, (cli, val, sit, dt) in enumerate(linhas):
            self.tabela.setItem(i, 0, QTableWidgetItem(cli))
            self.tabela.setItem(i, 1, QTableWidgetItem(f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
            self.tabela.setItem(i, 2, QTableWidgetItem(sit))
            self.tabela.setItem(i, 3, QTableWidgetItem(_date_to_str(dt)))
            
        self.lbl_total.setText(f"Total das notas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _exportar_excel(self):
        """Exporta Excel do relatório de notas de serviço."""
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Excel", "relatorio_notas_servico.xlsx", "Excel Files (*.xlsx)"
        )
        if not caminho:
            return
        
        data_inicio, data_fim = self.date_filter.get_date_range()
        ordens = self.sistema.listar_ordens_servico_por_data(data_inicio, data_fim)
        
        colunas = ["Cliente", "Valor", "Situação", "Data"]
        linhas = []
        total = 0.0
        
        for n in ordens:
            sit = "Paga" if n.foi_pago else "Não paga"
            linhas.append((n.cliente, n.valor_total, sit, n.data))
            total += n.valor_total
        
        modo = self.date_filter.get_modo_texto()
        periodo = "Todos os registros" if modo == "Tudo" else self.date_filter.lbl_info.text()
        saldo = f"Total das notas: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        sucesso = gerar_excel_relatorio(caminho, "Relatório de Notas de Serviço", periodo, saldo, colunas, linhas)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Excel exportado com sucesso!\n{caminho}")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao exportar Excel.")


# ===================== RELATÓRIO GERAL =====================

class RelatorioGeralDialog(BaseRelatorioDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(sistema, "Relatório geral", parent)
        
        # Filtros extras
        self.layout_card.addWidget(self._add_date_filter())
        
        row_opts = QHBoxLayout()
        row_opts.addWidget(QLabel("Incluir:"))
        self.chk_receitas = QCheckBox("Receitas"); self.chk_receitas.setChecked(True)
        self.chk_despesas = QCheckBox("Despesas"); self.chk_despesas.setChecked(True)
        self.chk_notas = QCheckBox("Notas de serviço"); self.chk_notas.setChecked(True)
        
        row_opts.addWidget(self.chk_receitas)
        row_opts.addWidget(self.chk_despesas)
        row_opts.addWidget(self.chk_notas)
        
        self.btn_atualizar = QPushButton("Atualizar", objectName="secondaryButton")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        row_opts.addStretch()
        row_opts.addWidget(self.btn_atualizar)
        
        self.layout_card.addLayout(row_opts)
        
        self._setup_tabela(["Tipo", "ID", "Data / Situação", "Descrição", "Valor"])
        
        footer = QHBoxLayout()
        self.lbl_saldo = QLabel("Saldo (Receitas - Despesas): R$ 0,00")
        footer.addWidget(self.lbl_saldo)
        footer.addStretch()
        
        btn_excel = QPushButton("Exportar Excel", objectName="secondaryButton")
        btn_excel.clicked.connect(self._exportar_excel)
        footer.addWidget(btn_excel)
        
        self.layout_card.addLayout(footer)
        
        self.carregar_dados()

    def carregar_dados(self):
        data_inicio, data_fim = self.date_filter.get_date_range()
        
        self._linhas_raw = []
        linhas = [] # (tipo, id, data_sit, desc, valor)
        
        # Receitas
        if self.chk_receitas.isChecked():
            recebimentos = self.sistema.listar_recebimentos_por_data(data_inicio, data_fim)
            for r in recebimentos:
                linhas.append(("Receita", r.id, r.data, f"Recebimento ({r.forma_pagamento.value})", r.valor))
                self._linhas_raw.append({
                    "tipo": "Receita", "id": r.id, "data": r.data, 
                    "descricao": f"Recebimento ({r.forma_pagamento.value})",
                    "valor": r.valor, "forma_pagamento": r.forma_pagamento.value,
                    "comprovante": r.comprovante_caminho
                })

        # Despesas
        if self.chk_despesas.isChecked():
            despesas = self.sistema.listar_despesas_por_data(data_inicio, data_fim)
            for d in despesas:
                # Valor negativo visualmente
                linhas.append(("Despesa", d.id, d.data, d.descricao, -abs(d.valor)))
                self._linhas_raw.append({
                    "tipo": "Despesa", "id": d.id, "data": d.data,
                    "descricao": d.descricao, "valor": d.valor,
                    "forma_pagamento": d.forma_pagamento.value,
                    "eh_a_prazo": d.eh_a_prazo, "data_vencimento": d.data_vencimento,
                    "comprovante": d.comprovante_caminho
                })
                
        # Notas
        if self.chk_notas.isChecked():
            ordens = self.sistema.listar_ordens_servico_por_data(data_inicio, data_fim)
            for n in ordens:
                sit = "Paga" if n.foi_pago else "Em aberto"
                data_sit = f"{_date_to_str(n.data)} - {sit}"
                linhas.append(("Nota de serviço", n.id, data_sit, n.descricao, n.valor_total))
                
                fp = n.forma_pagamento.value if n.forma_pagamento else "Não definido"
                self._linhas_raw.append({
                    "tipo": "Nota de serviço", "id": n.id, "data": n.data,
                    "cliente": n.cliente, "descricao": n.descricao,
                    "valor": n.valor_total, "situacao": sit,
                    "forma_pagamento": fp,
                    "comprovante": None
                })

        self.tabela.setRowCount(len(linhas))
        for i, (tipo, _id, ds, desc, val) in enumerate(linhas):
            self.tabela.setItem(i, 0, QTableWidgetItem(tipo))
            self.tabela.setItem(i, 1, QTableWidgetItem(str(_id or "")))
            
            d_str = _date_to_str(ds) if isinstance(ds, date) else str(ds)
            self.tabela.setItem(i, 2, QTableWidgetItem(d_str))
            self.tabela.setItem(i, 3, QTableWidgetItem(desc))
            self.tabela.setItem(i, 4, QTableWidgetItem(f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))

        # Atualiza lado real do sistema (independente dos filtros visuais, geralmente)
        # Mas aqui, o cliente pode querer o saldo DO RELATÓRIO? 
        # O código original usava self.sistema.calcular_saldo() que é global.
        saldo = self.sistema.calcular_saldo()
        self.lbl_saldo.setText(f"Saldo (Receitas - Despesas): R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _exportar_excel(self):
        """Exporta Excel do relatório geral."""
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Excel", "relatorio_geral.xlsx", "Excel Files (*.xlsx)"
        )
        if not caminho:
            return
        
        data_inicio, data_fim = self.date_filter.get_date_range()
        
        colunas = ["Tipo", "ID", "Data / Situação", "Descrição", "Valor"]
        linhas = []
        total_receitas = 0.0
        total_despesas = 0.0
        
        # Receitas
        if self.chk_receitas.isChecked():
            recebimentos = self.sistema.listar_recebimentos_por_data(data_inicio, data_fim)
            for r in recebimentos:
                linhas.append(("Receita", str(r.id or ""), r.data, 
                              f"Recebimento ({r.forma_pagamento.value})", r.valor))
                total_receitas += r.valor
        
        # Despesas
        if self.chk_despesas.isChecked():
            despesas = self.sistema.listar_despesas_por_data(data_inicio, data_fim)
            for d in despesas:
                linhas.append(("Despesa", str(d.id or ""), d.data, 
                              d.descricao, -abs(d.valor)))
                total_despesas += d.valor
        
        # Notas
        if self.chk_notas.isChecked():
            ordens = self.sistema.listar_ordens_servico_por_data(data_inicio, data_fim)
            for n in ordens:
                sit = "Paga" if n.foi_pago else "Em aberto"
                data_sit = f"{_date_to_str(n.data)} - {sit}"
                linhas.append(("Nota de serviço", str(n.id or ""), data_sit, 
                              n.descricao, n.valor_total))
        
        modo = self.date_filter.get_modo_texto()
        periodo = "Todos os registros" if modo == "Tudo" else self.date_filter.lbl_info.text()
        saldo = total_receitas - total_despesas
        saldo_texto = f"Saldo (Receitas - Despesas): R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        sucesso = gerar_excel_relatorio(caminho, "Relatório Geral", periodo, saldo_texto, colunas, linhas)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Excel exportado com sucesso!\n{caminho}")
        else:
            QMessageBox.critical(self, "Erro", "Erro ao exportar Excel.")
