"""
Módulo de Adição (Add).

Contém os diálogos para registrar novas entradas:
- NovaReceitaDialog
- NovaDespesaDialog
- NovaNotaServicoDialog
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QLineEdit, QDateEdit, QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QObject, QEvent
from typing import Optional

from interface.styles import DIALOG_STYLES
from interface.helpers import (
    mapear_forma_pagamento, 
    _formatar_texto_moeda, 
    _texto_para_float_moeda, 
    qdate_to_date
)
from models import FormaPagamento

# ===================== ENTER KEY FILTER =====================

class EnterKeyFilter(QObject):
    """
    Filtro de evento para interceptar a tecla Enter em campos de entrada.
    
    Quando Enter é pressionado em um QLineEdit, move o foco para o próximo
    widget na cadeia de foco, em vez de fechar/submeter o diálogo.
    """
    
    def eventFilter(self, obj, event):
        """
        Intercepta eventos de teclado.
        
        Args:
            obj: O widget que recebeu o evento
            event: O evento
            
        Returns:
            True se o evento foi tratado, False caso contrário
        """
        # Verifica se é um evento de tecla pressionada
        if event.type() == QEvent.KeyPress:
            # Verifica se a tecla é Enter ou Return
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Só intercepta se for um QLineEdit (ou similar)
                if isinstance(obj, (QLineEdit,)):
                    # Move para o próximo widget no foco
                    next_widget = obj.nextInFocusChain()
                    if next_widget:
                        next_widget.setFocus()
                    return True  # Evento tratado
        
        # Deixa o evento seguir normalmente
        return super().eventFilter(obj, event)


# ===================== BASE DIALOG (Opcional, mas ajuda a evitar repetição) =====================
# Optei por manter as classes separadas para clareza, mas repare que elas compartilham
# muita estrutura (Card, Header, Footer).

# ===================== NOVA RECEITA =====================

class NovaReceitaDialog(QDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self._formatando_valor = False
        
        # Config padrão dos diálogos
        self.setObjectName("novaReceitaDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(640, 420)
        self.setStyleSheet(DIALOG_STYLES)

        # Instala o filtro de eventos para navegação com Enter
        self.enter_filter = EnterKeyFilter(self)

        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Header
        h_layout = QHBoxLayout()
        v_titles = QVBoxLayout()
        v_titles.addWidget(QLabel("Nova Receita", objectName="title"))
        v_titles.addWidget(QLabel("Preencha os dados para registrar um recebimento.", objectName="subtitle"))
        
        btn_close = QPushButton("✕", objectName="closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        h_layout.addLayout(v_titles)
        h_layout.addStretch()
        h_layout.addWidget(btn_close)
        layout.addLayout(h_layout)
        
        # Linha divisória
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Dados
        layout.addWidget(QLabel("Dados da receita", objectName="sectionTitle"))

        # Valor
        self.input_valor = QLineEdit(objectName="amountEdit")
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)
        self.input_valor.installEventFilter(self.enter_filter)  # Instala o filtro
        layout.addWidget(self.input_valor)

        # Comprovante
        layout.addWidget(QLabel("Comprovante", objectName="sectionTitle"))
        
        comp_row = QHBoxLayout()
        comp_row.setSpacing(0)
        comp_row.setContentsMargins(0,0,0,0)
        
        self.input_comprovante = QLineEdit(objectName="fileEdit")
        self.input_comprovante.setPlaceholderText("Selecionar arquivo (opcional)")
        self.input_comprovante.setReadOnly(True)
        self.input_comprovante.setFixedHeight(44)
        
        btn_file = QPushButton("▼", objectName="fileButton")
        btn_file.setFixedSize(44, 44)
        btn_file.clicked.connect(self._selecionar_arquivo)
        
        comp_row.addWidget(self.input_comprovante)
        comp_row.addWidget(btn_file)
        
        frame_comp = QFrame(objectName="comprovanteFrame")
        frame_comp.setLayout(comp_row)
        layout.addWidget(frame_comp)

        # Forma Pagamento e Data
        row_opts = QHBoxLayout()
        
        col_fp = QVBoxLayout()
        col_fp.addWidget(QLabel("Forma de pagamento", objectName="sectionTitle"))
        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Escolher", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"])
        self.combo_fp.setFixedHeight(44)
        col_fp.addWidget(self.combo_fp)
        
        col_dt = QVBoxLayout()
        col_dt.addWidget(QLabel("Data", objectName="sectionTitle"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(44)
        col_dt.addWidget(self.date_edit)
        
        row_opts.addLayout(col_fp)
        row_opts.addLayout(col_dt)
        layout.addLayout(row_opts)

        # Botões
        layout.addSpacing(8)
        row_btns = QHBoxLayout()
        row_btns.addStretch()
        
        btn_cancel = QPushButton("Cancelar", objectName="secondaryButton")
        btn_cancel.setFixedHeight(46)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Salvar receita", objectName="primaryButton")
        btn_save.setFixedHeight(46)
        btn_save.clicked.connect(self._salvar)
        
        row_btns.addWidget(btn_cancel)
        row_btns.addWidget(btn_save)
        layout.addLayout(row_btns)

        root.addWidget(card)

    def _on_valor_edited(self, text):
        if self._formatando_valor: return
        fmt = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(fmt)
        self.input_valor.setCursorPosition(len(fmt))
        self._formatando_valor = False

    def _selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar comprovante")
        if arquivo:
            self.input_comprovante.setText(arquivo)

    def _salvar(self):
        valor_txt = self.input_valor.text().strip()
        if not valor_txt:
            QMessageBox.warning(self, "Aviso", "Informe o valor.")
            return
        
        try: valor = _texto_para_float_moeda(valor_txt)
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Valor inválido.")
            return

        if self.combo_fp.currentIndex() <= 0:
            QMessageBox.warning(self, "Aviso", "Selecione a forma de pagamento.")
            return
            
        fp_enum = mapear_forma_pagamento(self.combo_fp.currentText())
        if not fp_enum:
            QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
            return

        data_py = qdate_to_date(self.date_edit.date())
        comp = self.input_comprovante.text().strip() or None

        try:
            self.sistema.registrar_recebimento(valor, fp_enum, data_py, comp)
            QMessageBox.information(self, "Sucesso", "Receita registrada!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro: {e}")


# ===================== NOVA DESPESA =====================

class NovaDespesaDialog(QDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self._formatando_valor = False
        
        self.setObjectName("novaDespesaDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(680, 520)
        self.setStyleSheet(DIALOG_STYLES)

        # Instala o filtro de eventos para navegação com Enter
        self.enter_filter = EnterKeyFilter(self)

        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame(objectName="card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Header
        h_head = QHBoxLayout()
        v_h = QVBoxLayout()
        v_h.addWidget(QLabel("Nova Despesa", objectName="title"))
        v_h.addWidget(QLabel("Preencha os dados para registrar uma despesa.", objectName="subtitle"))
        btn_close = QPushButton("✕", objectName="closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)
        h_head.addLayout(v_h)
        h_head.addStretch()
        h_head.addWidget(btn_close)
        layout.addLayout(h_head)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Valor
        layout.addWidget(QLabel("Dados da despesa", objectName="sectionTitle"))
        self.input_valor = QLineEdit(objectName="amountEdit")
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)
        self.input_valor.installEventFilter(self.enter_filter)
        layout.addWidget(self.input_valor)

        # Descrição
        layout.addWidget(QLabel("Descrição", objectName="sectionTitle"))
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Ex: Conta de luz")
        self.input_desc.setFixedHeight(44)
        self.input_desc.installEventFilter(self.enter_filter)
        layout.addWidget(self.input_desc)

        # Comprovante
        layout.addWidget(QLabel("Comprovante", objectName="sectionTitle"))
        comp_frame = QFrame(objectName="comprovanteFrame")
        comp_layout = QHBoxLayout(comp_frame)
        comp_layout.setContentsMargins(0,0,0,0)
        comp_layout.setSpacing(0)
        
        self.input_comp = QLineEdit(objectName="fileEdit")
        self.input_comp.setPlaceholderText("Selecionar arquivo")
        self.input_comp.setReadOnly(True)
        self.input_comp.setFixedHeight(44)
        
        btn_file = QPushButton("▼", objectName="fileButton")
        btn_file.setFixedSize(44, 44)
        btn_file.clicked.connect(self._selecionar_arquivo)
        
        comp_layout.addWidget(self.input_comp)
        comp_layout.addWidget(btn_file)
        layout.addWidget(comp_frame)

        # FP e Data
        row_mid = QHBoxLayout()
        
        col_fp = QVBoxLayout()
        col_fp.addWidget(QLabel("Forma de pagamento", objectName="sectionTitle"))
        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Escolher", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"])
        self.combo_fp.setFixedHeight(44)
        col_fp.addWidget(self.combo_fp)
        
        col_dt = QVBoxLayout()
        col_dt.addWidget(QLabel("Data lançamento", objectName="sectionTitle"))
        self.dt_lanc = QDateEdit()
        self.dt_lanc.setCalendarPopup(True)
        self.dt_lanc.setDate(QDate.currentDate())
        self.dt_lanc.setFixedHeight(44)
        col_dt.addWidget(self.dt_lanc)
        
        row_mid.addLayout(col_fp)
        row_mid.addLayout(col_dt)
        layout.addLayout(row_mid)

        # A prazo
        row_prazo = QHBoxLayout()
        self.chk_prazo = QCheckBox("Despesa a prazo", objectName="prazoCheck")
        self.chk_prazo.stateChanged.connect(self._toggle_prazo)
        
        col_venc = QVBoxLayout()
        self.lbl_venc = QLabel("Data de vencimento", objectName="sectionTitle")
        self.dt_venc = QDateEdit()
        self.dt_venc.setCalendarPopup(True)
        self.dt_venc.setDate(QDate.currentDate())
        self.dt_venc.setFixedHeight(44)
        self.dt_venc.setEnabled(False) # começa desabilitado
        col_venc.addWidget(self.lbl_venc)
        col_venc.addWidget(self.dt_venc)
        
        row_prazo.addWidget(self.chk_prazo)
        row_prazo.addLayout(col_venc)
        layout.addLayout(row_prazo)

        # Botões
        layout.addSpacing(8)
        row_btns = QHBoxLayout()
        row_btns.addStretch()
        
        btn_cancel = QPushButton("Cancelar", objectName="secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Salvar despesa", objectName="primaryButton")
        btn_save.clicked.connect(self._salvar)
        
        row_btns.addWidget(btn_cancel)
        row_btns.addWidget(btn_save)
        layout.addLayout(row_btns)

        root.addWidget(card)

    def _on_valor_edited(self, text):
        if self._formatando_valor: return
        fmt = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(fmt)
        self.input_valor.setCursorPosition(len(fmt))
        self._formatando_valor = False

    def _selecionar_arquivo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Comprovante")
        if f: self.input_comp.setText(f)

    def _toggle_prazo(self, state):
        self.dt_venc.setEnabled(self.chk_prazo.isChecked())

    def _salvar(self):
        # Validações básicas omitidas para brevidade, mas devem existir
        valor_txt = self.input_valor.text().strip()
        desc = self.input_desc.text().strip()
        if not valor_txt or not desc or self.combo_fp.currentIndex() <= 0:
            QMessageBox.warning(self, "Aviso", "Preencha valor, descrição e forma de pagamento.")
            return
            
        valor = _texto_para_float_moeda(valor_txt)
        fp = mapear_forma_pagamento(self.combo_fp.currentText())
        dt_lanc = qdate_to_date(self.dt_lanc.date())
        comp = self.input_comp.text().strip() or None
        
        try:
            if self.chk_prazo.isChecked():
                dt_venc = qdate_to_date(self.dt_venc.date())
                self.sistema.registrar_despesa_a_prazo(valor, desc, fp, dt_venc, dt_lanc, comp)
            else:
                self.sistema.registrar_despesa(valor, desc, fp, dt_lanc, comp)
                
            QMessageBox.information(self, "Sucesso", "Despesa salva!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))


# ===================== NOVA NOTA DE SERVIÇO =====================

class NovaNotaServicoDialog(QDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self._formatando_valor = False
        
        self.setObjectName("novaNotaServicoDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(680, 520)
        self.setStyleSheet(DIALOG_STYLES)
        
        # Instala o filtro de eventos para navegação com Enter
        self.enter_filter = EnterKeyFilter(self)
        
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setAlignment(Qt.AlignCenter)
        
        card = QFrame(objectName="card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32,24,32,24)
        
        # Header
        h = QHBoxLayout()
        v = QVBoxLayout()
        v.addWidget(QLabel("Nova nota de serviço", objectName="title"))
        v.addWidget(QLabel("Cadastre uma ordem de serviço.", objectName="subtitle"))
        btn = QPushButton("✕", objectName="closeButton")
        btn.setFixedSize(40,40)
        btn.clicked.connect(self.close)
        h.addLayout(v)
        h.addStretch()
        h.addWidget(btn)
        layout.addLayout(h)
        
        layout.addWidget(self._linha())
        
        # Campos
        layout.addWidget(QLabel("Cliente", objectName="sectionTitle"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setFixedHeight(44)
        self.input_cliente.installEventFilter(self.enter_filter)
        layout.addWidget(self.input_cliente)
        
        layout.addWidget(QLabel("Descrição", objectName="sectionTitle"))
        self.input_desc = QLineEdit()
        self.input_desc.setFixedHeight(44)
        self.input_desc.installEventFilter(self.enter_filter)
        layout.addWidget(self.input_desc)

        layout.addWidget(QLabel("Data do serviço", objectName="sectionTitle"))
        self.dt_servico = QDateEdit()
        self.dt_servico.setCalendarPopup(True)
        self.dt_servico.setDate(QDate.currentDate())
        self.dt_servico.setFixedHeight(44)
        layout.addWidget(self.dt_servico)
        
        layout.addWidget(QLabel("Valor total", objectName="sectionTitle"))
        self.input_valor = QLineEdit(objectName="amountEdit")
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)
        self.input_valor.installEventFilter(self.enter_filter)
        layout.addWidget(self.input_valor)
        
        # Pagamento
        row_pag = QHBoxLayout()
        
        col_fp = QVBoxLayout()
        col_fp.addWidget(QLabel("Forma de pagamento", objectName="sectionTitle"))
        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Não definido", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"])
        self.combo_fp.setFixedHeight(44)
        col_fp.addWidget(self.combo_fp)
        
        col_pg = QVBoxLayout()
        col_pg.addWidget(QLabel("Situação", objectName="sectionTitle"))
        self.chk_pago = QCheckBox("Marcar como paga", objectName="PagoCheck")
        col_pg.addWidget(self.chk_pago)
        
        row_pag.addLayout(col_fp)
        row_pag.addLayout(col_pg)
        layout.addLayout(row_pag)
        
        # Botões
        layout.addSpacing(8)
        b_row = QHBoxLayout()
        b_row.addStretch()
        bc = QPushButton("Cancelar", objectName="secondaryButton")
        bc.clicked.connect(self.reject)
        bs = QPushButton("Salvar nota", objectName="primaryButton")
        bs.clicked.connect(self._salvar)
        b_row.addWidget(bc)
        b_row.addWidget(bs)
        layout.addLayout(b_row)

        root.addWidget(card)

    def _linha(self):
        l = QFrame()
        l.setFrameShape(QFrame.HLine)
        l.setFrameShadow(QFrame.Sunken)
        return l

    def _on_valor_edited(self, text):
        if self._formatando_valor: return
        fmt = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(fmt)
        self.input_valor.setCursorPosition(len(fmt))
        self._formatando_valor = False

    def _salvar(self):
        cliente = self.input_cliente.text().strip()
        desc = self.input_desc.text().strip()
        valor_txt = self.input_valor.text()
        
        if not cliente or not desc or not valor_txt:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos obrigatórios.")
            return
            
        valor = _texto_para_float_moeda(valor_txt)
        dt = qdate_to_date(self.dt_servico.date())
        pago = self.chk_pago.isChecked()
        
        fp = None
        if self.combo_fp.currentIndex() > 0:
            fp = mapear_forma_pagamento(self.combo_fp.currentText())
        
        if pago and not fp:
            QMessageBox.warning(self, "Aviso", "Se está pago, selecione a forma de pagamento.")
            return
            
        try:
            self.sistema.gerar_ordem_servico(cliente, desc, valor, pago, fp, dt)
            QMessageBox.information(self, "Sucesso", "Nota salva!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
