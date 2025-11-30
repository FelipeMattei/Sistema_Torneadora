"""
Módulo da interface com o usuário.

Responsável por exibir telas, menus ou janelas (seja no terminal,
Tkinter, PyQt, etc.) e coletar as ações do usuário. A interface chama
os métodos da camada de serviços (services.py) para executar ações
reais no sistema, sem se preocupar com detalhes de banco de dados
ou regras internas de negócio.
"""

# ===================== CONFIGURAÇÃO DE FONTE =====================
# Se você estiver usando Segoe UI via app.py, deixe vazio.
CUSTOM_FONT_PATH = ""  # r"fonts\Poppins\Poppins-Medium.ttf"
# ================================================================

import os
import sys
from typing import Optional
from datetime import date as _date, date

from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QSplitter,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QFrame,
    QFileDialog,
    QDialog,
    QMessageBox,
    QCheckBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPixmap, QPainter

from services import SistemaFinanceiro
from models import FormaPagamento, Recebimento, Despesa, OrdemServico
from database import Database


# ===================== ESTILOS COMUNS (QSS) =====================

DIALOG_STYLES = """
/* Só esses 3 diálogos terão fundo transparente */
QDialog#novaReceitaDialog,
QDialog#novaDespesaDialog,
QDialog#novaNotaServicoDialog,
QDialog#relatorioGeralDialog {
    background: transparent;
}

* {
    font-size: 15px;
}

QFrame#card {
    background-color: #E6E6E6;
    border-radius: 26px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 800;
    color: #3D3D3D;
}

QLabel#subtitle {
    font-size: 17px;
    color: #555555;
}

QLabel#sectionTitle {
    font-size: 17px;
    font-weight: 700;
    color: #4A4A4A;
    margin-top: 12px;
    margin-bottom: 6px;
}

/* Campos base (inputs, combo e data) */
QLineEdit, QComboBox, QDateEdit {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #d0d0d0;
    padding: 8px 12px;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
}

/* Foco (borda verde suave) */
QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus {
    border: 1px solid #00b33c;
}

/* Combobox: aparência do cabeçalho */
QComboBox {
    padding: 8px 40px 8px 14px;
    color: #555555;
}

/* Popup da combobox (lista de opções) */
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #d0d0d0;
    outline: 0;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
}

QComboBox QAbstractItemView::item {
    padding: 4px 16px;
}

/* área da direita onde fica a seta do combo */
QComboBox::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}

/* ícone da seta do combo */
QComboBox::down-arrow {
    image: url(icons/right-arrow.png);
    width: 14px;
    height: 14px;
}

/* DateEdit: mesma cara do combo, só ajusta espaço pra seta */
QDateEdit {
    padding-right: 32px;
}

QDateEdit::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}

QDateEdit::down-arrow {
    image: url(icons/right-arrow.png);
    width: 14px;
    height: 14px;
}

QPushButton#closeButton {
    border: none;
    background: transparent;
    font-size: 16px;
}
QPushButton#closeButton:hover {
    background-color: rgba(0,0,0,0.06);
    border-radius: 10px;
}

QPushButton#fileButton {
    background-color: #ffffff;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    border: 1px solid #d0d0d0;
}

/* "Colar" input de comprovante no botão ▼ */
QFrame#comprovanteFrame QLineEdit {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    border-right: none;
}
QPushButton#fileButton {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
}

QPushButton#primaryButton {
    background-color: #00b33c;
    color: white;
    border-radius: 10px;
    padding: 10px 25px;
    border: 1px solid #9F9F9F;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background-color: #00a534;
}

QPushButton#secondaryButton {
    background-color: #d9d9d9;
    color: #555555;
    border-radius: 10px;
    padding: 10px 38px;
    border: 1px;
    font-weight: 600;
}
QPushButton#secondaryButton:hover {
    background-color: #cfcfcf;
}

/* Checkbox de "Despesa a prazo" maior */
QCheckBox#prazoCheck {
    font-size: 17px;            /* aumenta o texto */
    font-weight: 700;
    color: #4A4A4A;
}

/* aumenta o quadradinho da marcação */
QCheckBox#prazoCheck::indicator {
    margin-top: 0px;
}

/* Checkbox de "Marcar como paga" maior */
QCheckBox#PagoCheck {
    font-size: 15px;            /* aumenta o texto */
    font-weight: 700;
    color: #4A4A4A;
}

/* aumenta o quadradinho da marcação */
QCheckBox#PagoCheck::indicator {
    margin-top: 0px;
}
"""


# ===================== HELPERS COMUNS =====================

def mapear_forma_pagamento(texto: str) -> Optional[FormaPagamento]:
    t = texto.strip().lower()
    mapa = {
        "dinheiro": FormaPagamento.DINHEIRO,
        "débito": FormaPagamento.DEBITO,
        "debito": FormaPagamento.DEBITO,
        "crédito": FormaPagamento.CREDITO,
        "credito": FormaPagamento.CREDITO,
        "pix": FormaPagamento.PIX,
        "boleto": FormaPagamento.BOLETO,
        "cheque": FormaPagamento.CHEQUE,
    }
    return mapa.get(t)


def _formatar_texto_moeda(texto: str) -> str:
    """
    Recebe um texto qualquer e devolve no formato:
    'R$ 1.234,56'
    """
    cleaned = (
        texto.replace("R", "")
             .replace("$", "")
             .replace(" ", "")
             .replace(".", "")
             .replace(",", "")
    )
    digits = "".join(ch for ch in cleaned if ch.isdigit())

    if not digits:
        return ""

    if len(digits) == 1:
        digits = "0" + digits

    inteiros = digits[:-2]
    centavos = digits[-2:]

    if not inteiros:
        inteiros = "0"

    inteiros_int = int(inteiros)
    inteiros_formatado = f"{inteiros_int:,}".replace(",", ".")

    return f"R$ {inteiros_formatado},{centavos}"


def _texto_para_float_moeda(texto: str) -> float:
    """
    'R$ 1.234,56' -> 1234.56
    """
    txt = texto.strip()
    if txt.lower().startswith("r$"):
        txt = txt[2:].strip()
    normalizado = txt.replace(".", "").replace(",", ".")
    return float(normalizado)


def qdate_to_date(qd: QDate) -> _date:
    """Converte QDate para datetime.date de forma segura."""
    try:
        return qd.toPython()
    except AttributeError:
        return _date(qd.year(), qd.month(), qd.day())


# ===================== DIALOGO: NOVA RECEITA =====================

class NovaReceitaDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)

        self.sistema = sistema
        self._formatando_valor = False
        self.setObjectName("novaReceitaDialog")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Nova Receita")
        title.setObjectName("title")

        subtitle = QLabel("Preencha os dados para registrar um recebimento.")
        subtitle.setObjectName("subtitle")

        header_text_layout = QVBoxLayout()
        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        card_layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Dados da receita
        section1_label = QLabel("Dados da receita")
        section1_label.setObjectName("sectionTitle")
        card_layout.addWidget(section1_label)

        amount_frame = QFrame()
        amount_frame.setObjectName("amountFrame")
        amount_layout = QHBoxLayout(amount_frame)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_layout.setSpacing(0)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setObjectName("amountEdit")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)

        amount_layout.addWidget(self.input_valor)
        card_layout.addWidget(amount_frame)

        # Comprovante
        section2_label = QLabel("Comprovante")
        section2_label.setObjectName("sectionTitle")
        card_layout.addWidget(section2_label)

        comprovante_frame = QFrame()
        comprovante_frame.setObjectName("comprovanteFrame")
        comprovante_layout = QHBoxLayout(comprovante_frame)
        comprovante_layout.setContentsMargins(0, 0, 0, 0)
        comprovante_layout.setSpacing(0)

        self.input_comprovante = QLineEdit()
        self.input_comprovante.setPlaceholderText("Selecionar arquivo (opcional)")
        self.input_comprovante.setReadOnly(True)
        self.input_comprovante.setObjectName("fileEdit")
        self.input_comprovante.setFixedHeight(44)

        btn_comprovante = QPushButton("▼")
        btn_comprovante.setObjectName("fileButton")
        btn_comprovante.setFixedWidth(44)
        btn_comprovante.setFixedHeight(44)
        btn_comprovante.clicked.connect(self.selecionar_arquivo)

        comprovante_layout.addWidget(self.input_comprovante)
        comprovante_layout.addWidget(btn_comprovante)
        card_layout.addWidget(comprovante_frame)

        # Forma de pagamento / Data
        row_fp_data = QHBoxLayout()
        row_fp_data.setSpacing(16)

        col_fp = QVBoxLayout()
        lbl_fp = QLabel("Forma de pagamento")
        lbl_fp.setObjectName("sectionTitle")

        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Escolher", "Dinheiro", "Débito", "Crédito", "PIX"])
        self.combo_fp.setFixedHeight(44)

        col_fp.addWidget(lbl_fp)
        col_fp.addWidget(self.combo_fp)

        col_data = QVBoxLayout()
        lbl_data = QLabel("Data")
        lbl_data.setObjectName("sectionTitle")

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(44)

        col_data.addWidget(lbl_data)
        col_data.addWidget(self.date_edit)

        row_fp_data.addLayout(col_fp)
        row_fp_data.addLayout(col_data)
        card_layout.addLayout(row_fp_data)

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setFixedHeight(46)

        btn_salvar = QPushButton("Salvar receita")
        btn_salvar.setObjectName("primaryButton")
        btn_salvar.setFixedHeight(46)

        btn_cancelar.clicked.connect(self.reject)
        btn_salvar.clicked.connect(self.salvar_receita)

        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(btn_salvar)

        card_layout.addSpacing(8)
        card_layout.addLayout(btn_row)

        root_layout.addWidget(self.card)

        self.setStyleSheet(DIALOG_STYLES)
        self.resize(640, 420)

    # --- lógica de formatação de moeda ---
    def _on_valor_edited(self, text: str):
        if self._formatando_valor:
            return

        valor_formatado = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(valor_formatado)
        self.input_valor.setCursorPosition(len(valor_formatado))
        self._formatando_valor = False

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar comprovante")
        if arquivo:
            self.input_comprovante.setText(arquivo)

    def salvar_receita(self):
        valor_txt = self.input_valor.text().strip()
        if not valor_txt:
            QMessageBox.warning(self, "Dados incompletos", "Informe o valor da receita.")
            return

        try:
            valor = _texto_para_float_moeda(valor_txt)
        except ValueError:
            QMessageBox.warning(self, "Valor inválido", "Digite um número válido para o valor.")
            return

        if self.combo_fp.currentIndex() <= 0:
            QMessageBox.warning(self, "Dados incompletos", "Selecione a forma de pagamento.")
            return

        fp_text = self.combo_fp.currentText()
        forma_pagamento = mapear_forma_pagamento(fp_text)
        if forma_pagamento is None:
            QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
            return

        data_py = qdate_to_date(self.date_edit.date())
        comprovante = self.input_comprovante.text().strip() or None

        try:
            self.sistema.registrar_recebimento(
                valor=valor,
                forma_pagamento=forma_pagamento,
                data=data_py,
                comprovante_caminho=comprovante,
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Ocorreu um erro ao salvar a receita:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", "Receita registrada com sucesso!")
        self.accept()


# ===================== DIALOGO: NOVA DESPESA =====================

class NovaDespesaDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)

        self.sistema = sistema
        self._formatando_valor = False
        self.setObjectName("novaDespesaDialog")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Nova Despesa")
        title.setObjectName("title")

        subtitle = QLabel("Preencha os dados para registrar uma despesa.")
        subtitle.setObjectName("subtitle")

        header_text_layout = QVBoxLayout()
        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        card_layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Dados da despesa
        section1_label = QLabel("Dados da despesa")
        section1_label.setObjectName("sectionTitle")
        card_layout.addWidget(section1_label)

        amount_frame = QFrame()
        amount_frame.setObjectName("amountFrame")
        amount_layout = QHBoxLayout(amount_frame)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_layout.setSpacing(0)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setObjectName("amountEdit")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)

        amount_layout.addWidget(self.input_valor)
        card_layout.addWidget(amount_frame)

        # Descrição
        lbl_desc = QLabel("Descrição")
        lbl_desc.setObjectName("sectionTitle")
        card_layout.addWidget(lbl_desc)

        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Ex: Conta de luz, compra de material, etc.")
        self.input_descricao.setFixedHeight(44)
        card_layout.addWidget(self.input_descricao)

        # Comprovante
        section2_label = QLabel("Comprovante")
        section2_label.setObjectName("sectionTitle")
        card_layout.addWidget(section2_label)

        comprovante_frame = QFrame()
        comprovante_frame.setObjectName("comprovanteFrame")
        comprovante_layout = QHBoxLayout(comprovante_frame)
        comprovante_layout.setContentsMargins(0, 0, 0, 0)
        comprovante_layout.setSpacing(0)

        self.input_comprovante = QLineEdit()
        self.input_comprovante.setPlaceholderText("Selecionar arquivo (opcional)")
        self.input_comprovante.setReadOnly(True)
        self.input_comprovante.setObjectName("fileEdit")
        self.input_comprovante.setFixedHeight(44)

        btn_comprovante = QPushButton("▼")
        btn_comprovante.setObjectName("fileButton")
        btn_comprovante.setFixedWidth(44)
        btn_comprovante.setFixedHeight(44)
        btn_comprovante.clicked.connect(self.selecionar_arquivo)

        comprovante_layout.addWidget(self.input_comprovante)
        comprovante_layout.addWidget(btn_comprovante)
        card_layout.addWidget(comprovante_frame)

        # Forma de pagamento / Data lançamento
        row_fp_data = QHBoxLayout()
        row_fp_data.setSpacing(16)

        col_fp = QVBoxLayout()
        lbl_fp = QLabel("Forma de pagamento")
        lbl_fp.setObjectName("sectionTitle")

        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Escolher", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"])
        self.combo_fp.setFixedHeight(44)

        col_fp.addWidget(lbl_fp)
        col_fp.addWidget(self.combo_fp)

        col_data = QVBoxLayout()
        lbl_data = QLabel("Data de lançamento")
        lbl_data.setObjectName("sectionTitle")

        self.date_lancamento = QDateEdit()
        self.date_lancamento.setCalendarPopup(True)
        self.date_lancamento.setDate(QDate.currentDate())
        self.date_lancamento.setFixedHeight(44)

        col_data.addWidget(lbl_data)
        col_data.addWidget(self.date_lancamento)

        row_fp_data.addLayout(col_fp)
        row_fp_data.addLayout(col_data)
        card_layout.addLayout(row_fp_data)

        # A prazo?
        row_prazo = QHBoxLayout()
        row_prazo.setSpacing(16)

        self.chk_prazo = QCheckBox("Despesa a prazo")
        self.chk_prazo.setChecked(False)
        self.chk_prazo.setObjectName("prazoCheck")  # <- nome único
        self.chk_prazo.stateChanged.connect(self._toggle_prazo)

        col_venc = QVBoxLayout()
        lbl_venc = QLabel("Data de vencimento")
        lbl_venc.setObjectName("sectionTitle")

        self.date_vencimento = QDateEdit()
        self.date_vencimento.setCalendarPopup(True)
        self.date_vencimento.setDate(QDate.currentDate())
        self.date_vencimento.setFixedHeight(44)

        col_venc.addWidget(lbl_venc)
        col_venc.addWidget(self.date_vencimento)

        row_prazo.addWidget(self.chk_prazo)
        row_prazo.addLayout(col_venc)
        card_layout.addLayout(row_prazo)

        # por padrão, desabilita vencimento
        self._toggle_prazo(self.chk_prazo.checkState())

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setFixedHeight(46)

        btn_salvar = QPushButton("Salvar despesa")
        btn_salvar.setObjectName("primaryButton")
        btn_salvar.setFixedHeight(46)

        btn_cancelar.clicked.connect(self.reject)
        btn_salvar.clicked.connect(self.salvar_despesa)

        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(btn_salvar)

        card_layout.addSpacing(8)
        card_layout.addLayout(btn_row)

        root_layout.addWidget(self.card)

        self.setStyleSheet(DIALOG_STYLES)
        self.resize(680, 480)

    def _toggle_prazo(self, state):
        is_prazo = self.chk_prazo.isChecked()
        self.date_vencimento.setEnabled(is_prazo)

    def _on_valor_edited(self, text: str):
        if self._formatando_valor:
            return
        valor_formatado = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(valor_formatado)
        self.input_valor.setCursorPosition(len(valor_formatado))
        self._formatando_valor = False

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar comprovante")
        if arquivo:
            self.input_comprovante.setText(arquivo)

    def salvar_despesa(self):
        valor_txt = self.input_valor.text().strip()
        if not valor_txt:
            QMessageBox.warning(self, "Dados incompletos", "Informe o valor da despesa.")
            return

        try:
            valor = _texto_para_float_moeda(valor_txt)
        except ValueError:
            QMessageBox.warning(self, "Valor inválido", "Digite um número válido para o valor.")
            return

        descricao = self.input_descricao.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Dados incompletos", "Informe uma descrição para a despesa.")
            return

        if self.combo_fp.currentIndex() <= 0:
            QMessageBox.warning(self, "Dados incompletos", "Selecione a forma de pagamento.")
            return

        forma_pagamento = mapear_forma_pagamento(self.combo_fp.currentText())
        if forma_pagamento is None:
            QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
            return

        # Data lançamento
        data_lanc = qdate_to_date(self.date_lancamento.date())
        comprovante = self.input_comprovante.text().strip() or None

        try:
            if not self.chk_prazo.isChecked():
                # Despesa à vista
                self.sistema.registrar_despesa(
                    valor=valor,
                    descricao=descricao,
                    forma_pagamento=forma_pagamento,
                    data=data_lanc,
                    comprovante_caminho=comprovante,
                )
            else:
                # Despesa a prazo
                data_venc = qdate_to_date(self.date_vencimento.date())

                self.sistema.registrar_despesa_a_prazo(
                    valor=valor,
                    descricao=descricao,
                    forma_pagamento=forma_pagamento,
                    data_vencimento=data_venc,
                    data_lancamento=data_lanc,
                    comprovante_caminho=comprovante,
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Ocorreu um erro ao salvar a despesa:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", "Despesa registrado com sucesso!")
        self.accept()


# ===================== DIALOGO: NOVA NOTA DE SERVIÇO =====================

class NovaNotaServicoDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)

        self.sistema = sistema
        self._formatando_valor = False
        self.setObjectName("novaNotaServicoDialog")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Nova nota de serviço")
        title.setObjectName("title")

        subtitle = QLabel("Cadastre uma ordem/nota de serviço.")
        subtitle.setObjectName("subtitle")

        header_text_layout = QVBoxLayout()
        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        card_layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Cliente
        lbl_cliente = QLabel("Cliente")
        lbl_cliente.setObjectName("sectionTitle")
        card_layout.addWidget(lbl_cliente)

        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nome do cliente")
        self.input_cliente.setFixedHeight(44)
        card_layout.addWidget(self.input_cliente)

        # Descrição
        lbl_desc = QLabel("Descrição do serviço")
        lbl_desc.setObjectName("sectionTitle")
        card_layout.addWidget(lbl_desc)

        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Ex: Manutenção de torno, fabricação de peça, etc.")
        self.input_descricao.setFixedHeight(44)
        card_layout.addWidget(self.input_descricao)

        # Data do serviço  ⬅⬅⬅ NOVO
        lbl_data = QLabel("Data do serviço")
        lbl_data.setObjectName("sectionTitle")
        card_layout.addWidget(lbl_data)

        self.date_servico = QDateEdit()
        self.date_servico.setCalendarPopup(True)
        self.date_servico.setDate(QDate.currentDate())
        self.date_servico.setFixedHeight(44)
        card_layout.addWidget(self.date_servico)

        # Valor
        lbl_valor = QLabel("Valor total")
        lbl_valor.setObjectName("sectionTitle")
        card_layout.addWidget(lbl_valor)

        amount_frame = QFrame()
        amount_frame.setObjectName("amountFrame")
        amount_layout = QHBoxLayout(amount_frame)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_layout.setSpacing(0)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("R$ 0,00")
        self.input_valor.setObjectName("amountEdit")
        self.input_valor.setFixedHeight(44)
        self.input_valor.textEdited.connect(self._on_valor_edited)

        amount_layout.addWidget(self.input_valor)
        card_layout.addWidget(amount_frame)

        # Pagamento
        row_pag = QHBoxLayout()
        row_pag.setSpacing(16)

        col_fp = QVBoxLayout()
        lbl_fp = QLabel("Forma de pagamento")
        lbl_fp.setObjectName("sectionTitle")

        self.combo_fp = QComboBox()
        self.combo_fp.addItems(["Não definido", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"])
        self.combo_fp.setFixedHeight(44)

        col_fp.addWidget(lbl_fp)
        col_fp.addWidget(self.combo_fp)

        col_pago = QVBoxLayout()
        lbl_pago = QLabel("Situação")
        lbl_pago.setObjectName("sectionTitle")
        self.chk_pago = QCheckBox("Marcar como paga")
        self.chk_pago.setObjectName("PagoCheck")
        col_pago.addWidget(lbl_pago)
        col_pago.addWidget(self.chk_pago)

        row_pag.addLayout(col_fp)
        row_pag.addLayout(col_pago)
        card_layout.addLayout(row_pag)

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setFixedHeight(46)

        btn_salvar = QPushButton("Salvar nota de serviço")
        btn_salvar.setObjectName("primaryButton")
        btn_salvar.setFixedHeight(46)

        btn_cancelar.clicked.connect(self.reject)
        btn_salvar.clicked.connect(self.salvar_nota_servico)

        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(btn_salvar)

        card_layout.addSpacing(8)
        card_layout.addLayout(btn_row)

        root_layout.addWidget(self.card)

        self.setStyleSheet(DIALOG_STYLES)
        self.resize(680, 520)

    def _on_valor_edited(self, text: str):
        if self._formatando_valor:
            return
        valor_formatado = _formatar_texto_moeda(text)
        self._formatando_valor = True
        self.input_valor.setText(valor_formatado)
        self.input_valor.setCursorPosition(len(valor_formatado))
        self._formatando_valor = False

    def salvar_nota_servico(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Dados incompletos", "Informe o cliente.")
            return

        descricao = self.input_descricao.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Dados incompletos", "Informe a descrição do serviço.")
            return

        valor_txt = self.input_valor.text().strip()
        if not valor_txt:
            QMessageBox.warning(self, "Dados incompletos", "Informe o valor da nota de serviço.")
            return

        try:
            valor = _texto_para_float_moeda(valor_txt)
        except ValueError:
            QMessageBox.warning(self, "Valor inválido", "Digite um número válido para o valor.")
            return

        # Data do serviço
        data_servico = qdate_to_date(self.date_servico.date())

        foi_pago = self.chk_pago.isChecked()

        forma_pagamento: Optional[FormaPagamento] = None
        if self.combo_fp.currentIndex() > 0:
            forma_pagamento = mapear_forma_pagamento(self.combo_fp.currentText())
            if forma_pagamento is None:
                QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
                return
        else:
            # se marcar como paga mas não escolher forma, avisa
            if foi_pago:
                QMessageBox.warning(
                    self,
                    "Dados incompletos",
                    "Selecione a forma de pagamento ou desmarque 'Marcar como paga'.",
                )
                return

        try:
            # ⚠️ Aqui estou assumindo que você já ajustou gerar_ordem_servico
            # para receber um parâmetro `data: date`.
            self.sistema.gerar_ordem_servico(
                cliente=cliente,
                descricao=descricao,
                valor_total=valor,
                data=data_servico,
                foi_pago=foi_pago,
                forma_pagamento=forma_pagamento,
            )
        except TypeError:
            # Caso ainda não tenha o parâmetro data no services.py
            QMessageBox.critical(
                self,
                "Erro na chamada",
                "O método gerar_ordem_servico ainda não aceita o parâmetro 'data'.\n"
                "Confirme se o services.py foi atualizado para incluir data na Ordem de Serviço.",
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Ocorreu um erro ao salvar a nota de serviço:\n{e}")
            return

        QMessageBox.information(self, "Sucesso", "Nota de serviço registrada com sucesso!")
        self.accept()


# ===================== HELPERS DE RELATÓRIO =====================

from datetime import timedelta


def _limite_por_periodo(nome: str) -> Optional[date]:
    """
    Converte o texto do combo (Diário/Semanal/Mensal/Tudo)
    em uma data de corte (hoje - n dias). Se for 'Tudo', retorna None.
    """
    hoje = date.today()
    nome = nome.lower()

    if "diário" in nome or "diario" in nome:
        return hoje
    if "semanal" in nome:
        return hoje - timedelta(days=6)
    if "mensal" in nome:
        return hoje - timedelta(days=29)
    return None  # Tudo


def _date_to_str(d: Optional[date]) -> str:
    if not d:
        return ""
    return d.strftime("%d/%m/%Y")


def _bool_to_str(b: bool) -> str:
    return "Sim" if b else "Não"


class ZoomGraphicsView(QGraphicsView):
    """
    QGraphicsView com zoom via scroll do mouse e arrastar com o botão.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        self.scale(factor, factor)


class ImagemZoomDialog(QDialog):
    """
    Janela pra ver o comprovante em tela cheia, com zoom e pan.
    """
    def __init__(self, caminho_imagem: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Visualizar comprovante")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        pix = QPixmap(caminho_imagem)
        if pix.isNull():
            lbl = QLabel("Não foi possível carregar a imagem do comprovante.")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            return

        scene = QGraphicsScene(self)
        scene.addPixmap(pix)

        view = ZoomGraphicsView()
        view.setScene(scene)

        layout.addWidget(view)

        # deixa o usuário maximizar / tela cheia
        self.setWindowState(Qt.WindowMaximized)

class DetalheLancamentoDialog(QDialog):
    """
    Mostra os detalhes de um item do relatório (receita, despesa ou nota de serviço),
    com preview do comprovante (quando existir) e permite edição opcional.
    """

    def __init__(self, info: dict, parent=None):
        super().__init__(parent)

        self.info = info
        self._caminho_imagem = info.get("comprovante")
        self._sistema = getattr(parent, "sistema", None)

        # campos editáveis -> widgets de edição (QLineEdit, QDateEdit, QComboBox)
        self._campos_editaveis: dict[str, QWidget] = {}
        # labels de visualização (modo somente leitura)
        self._labels_valores: dict[str, QLabel] = {}

        self._modo_edicao = False
        self._formatando_valor = False

        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(12)  # um pouco mais compacto

        # ----------------- Cabeçalho -----------------
        header = QHBoxLayout()
        title = QLabel("Detalhes do lançamento")
        title.setObjectName("title")

        subtitle = QLabel("Todas as informações.")
        subtitle.setObjectName("subtitle")

        header_text = QVBoxLayout()
        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(btn_close)

        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # ----------------- Infos principais -----------------
        tipo = info.get("tipo", "-")

        # Tipo e ID apenas como texto
        self._add_label_simples(card_layout, "Tipo", tipo)
        self._add_label_simples(card_layout, "ID", info.get("id", "-"))

        # Campos variam por tipo
        if tipo == "Nota de serviço":
            self._montar_campos_nota_servico(card_layout, info)
        elif tipo == "Receita":
            self._montar_campos_receita(card_layout, info)
        elif tipo == "Despesa":
            self._montar_campos_despesa(card_layout, info)
        else:
            # fallback genérico
            data = info.get("data")
            data_str = _date_to_str(data) if isinstance(data, date) else "-"
            situacao = info.get("situacao")
            if situacao:
                data_str = f"{data_str} - {situacao}"

            self._add_label_simples(card_layout, "Data / Situação", data_str)
            self._add_label_simples(card_layout, "Descrição", info.get("descricao", "-"))
            valor = info.get("valor", 0.0)
            self._add_label_simples(
                card_layout,
                "Valor",
                "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

        # ----------------- Comprovante -----------------
        self.comp_frame = QFrame()
        comp_layout = QVBoxLayout(self.comp_frame)
        comp_layout.setContentsMargins(0, 8, 0, 0)
        comp_layout.setSpacing(8)

        lbl_comp = QLabel("Comprovante")
        lbl_comp.setObjectName("sectionTitle")
        comp_layout.addWidget(lbl_comp)

        self.lbl_comp_path = QLabel()
        self.lbl_comp_path.setWordWrap(True)
        comp_layout.addWidget(self.lbl_comp_path)

        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setFixedHeight(200)
        self.lbl_preview.setStyleSheet(
            "border: 1px solid #CCCCCC; border-radius: 8px; background-color: #F5F5F5;"
        )
        self.lbl_preview.setScaledContents(True)
        comp_layout.addWidget(self.lbl_preview)

        self.btn_ver_maior = QPushButton("Ver comprovante em tela cheia")
        self.btn_ver_maior.setObjectName("primaryButton")
        self.btn_ver_maior.setFixedHeight(42)
        self.btn_ver_maior.clicked.connect(self._abrir_zoom)
        comp_layout.addWidget(self.btn_ver_maior)

        card_layout.addWidget(self.comp_frame)

        # Nota de serviço não tem comprovante
        if tipo == "Nota de serviço":
            self.comp_frame.setVisible(False)
        else:
            self._carregar_imagem()

        # ----------------- Rodapé (Editar / Salvar / Fechar) -----------------
        card_layout.addSpacing(8)
        row_btn = QHBoxLayout()
        row_btn.addStretch()

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setObjectName("secondaryButton")
        self.btn_editar.setFixedHeight(42)
        self.btn_editar.clicked.connect(self._ativar_edicao)
        row_btn.addWidget(self.btn_editar)

        self.btn_salvar = QPushButton("Salvar alterações")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.setFixedHeight(42)
        self.btn_salvar.clicked.connect(self._salvar_alteracoes)
        self.btn_salvar.setEnabled(False)
        row_btn.addWidget(self.btn_salvar)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("secondaryButton")
        btn_fechar.setFixedHeight(42)
        btn_fechar.clicked.connect(self.reject)
        row_btn.addWidget(btn_fechar)

        card_layout.addLayout(row_btn)

        root.addWidget(card)
        self.setStyleSheet(DIALOG_STYLES)
        self.resize(720, 500)

    # ============================================================
    # Montagem dos campos por tipo
    # ============================================================

    def _montar_campos_receita(self, layout: QVBoxLayout, info: dict):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        forma = info.get("forma_pagamento", "Não definido")

        # Valor (editável, com máscara de moeda)
        valor_str = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_str = f"R$ {valor_str}"
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)

        # Data
        self._add_data_linha(layout, "Data", "data", data)

        # Forma de pagamento
        opcoes_fp = ["Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)

    def _montar_campos_despesa(self, layout: QVBoxLayout, info: dict):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        forma = info.get("forma_pagamento", "Não definido")
        descricao = info.get("descricao", "-")
        eh_a_prazo = bool(info.get("eh_a_prazo", False))
        data_venc = info.get("data_vencimento")

        valor_str = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_str = f"R$ {valor_str}"
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)

        self._add_data_linha(layout, "Data de lançamento", "data", data)

        opcoes_fp = ["Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)

        self._add_input_linha(layout, "Descrição", "descricao", descricao, is_valor=False)

        # Tipo de conta (à vista / a prazo)
        opcoes_conta = ["Conta à vista", "Conta a prazo"]
        atual = "Conta a prazo" if eh_a_prazo else "Conta à vista"
        self._add_combo_linha(layout, "Tipo de conta", "tipo_conta", opcoes_conta, atual)

        # Data de vencimento
        self._add_data_linha(layout, "Data de vencimento", "data_vencimento", data_venc)

    def _montar_campos_nota_servico(self, layout: QVBoxLayout, info: dict):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        cliente = info.get("cliente", "-")
        descricao = info.get("descricao", "-")
        situacao = info.get("situacao", "Não paga")
        forma = info.get("forma_pagamento", "Não definido")

        self._add_input_linha(layout, "Cliente", "cliente", cliente, is_valor=False)
        self._add_input_linha(layout, "Descrição do serviço", "descricao", descricao, is_valor=False)

        valor_str = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_str = f"R$ {valor_str}"
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)

        self._add_data_linha(layout, "Data", "data", data)

        opcoes_sit = ["Paga", "Não paga"]
        self._add_combo_linha(layout, "Situação", "situacao", opcoes_sit, situacao)

        opcoes_fp = ["Não definido", "Dinheiro", "Débito", "Crédito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)

    # ============================================================
    # Helpers de construção de campos
    # ============================================================

    def _add_label_simples(self, layout: QVBoxLayout, titulo: str, valor):
        lbl = QLabel(f"{titulo}: {valor}")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

    def _add_input_linha(self, layout: QVBoxLayout, titulo: str, chave: str,
                         valor_inicial: str, is_valor: bool = False):
        from PySide6.QtWidgets import QLineEdit

        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(6)

        lbl_titulo = QLabel(f"{titulo}:")
        lbl_valor = QLabel(str(valor_inicial))
        # se quiser, pode ajustar estilo dessa label com um objectName
        # lbl_valor.setObjectName("valueLabel")

        edit = QLineEdit()
        edit.setText(str(valor_inicial))
        edit.setReadOnly(True)      # inicialmente somente leitura
        edit.setVisible(False)      # e oculto (modo visualização usa lbl_valor)

        if is_valor:
            edit.setPlaceholderText("R$ 0,00")
            edit.textEdited.connect(self._on_valor_editado)

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(edit, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = edit
        self._labels_valores[chave] = lbl_valor

    def _add_data_linha(self, layout: QVBoxLayout, titulo: str, chave: str,
                        data_inicial: date | None):
        from PySide6.QtWidgets import QDateEdit

        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(6)

        lbl_titulo = QLabel(f"{titulo}:")

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)

        if isinstance(data_inicial, date):
            qd = QDate(data_inicial.year, data_inicial.month, data_inicial.day)
        else:
            qd = QDate.currentDate()

        date_edit.setDate(qd)
        date_edit.setEnabled(False)
        date_edit.setVisible(False)  # começa oculto

        lbl_valor = QLabel(qd.toString("dd/MM/yyyy"))

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(date_edit, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = date_edit
        self._labels_valores[chave] = lbl_valor

    def _add_combo_linha(self, layout: QVBoxLayout, titulo: str, chave: str,
                         opcoes: list[str], valor_atual: str | None):
        from PySide6.QtWidgets import QComboBox

        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(6)

        lbl_titulo = QLabel(f"{titulo}:")
        combo = QComboBox()
        combo.addItems(opcoes)

        if valor_atual is not None:
            idx = combo.findText(str(valor_atual), Qt.MatchFixedString)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        combo.setEnabled(False)       # começa travado
        combo.setVisible(False)       # e oculto

        texto_inicial = combo.currentText() if combo.currentIndex() >= 0 else "-"
        lbl_valor = QLabel(texto_inicial)

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(combo, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = combo
        self._labels_valores[chave] = lbl_valor

    # ============================================================
    # Modo edição / salvar
    # ============================================================

    def _ativar_edicao(self):
        if self._modo_edicao:
            return

        self._modo_edicao = True

        from PySide6.QtWidgets import QLineEdit, QDateEdit, QComboBox

        for chave, widget in self._campos_editaveis.items():
            label_view = self._labels_valores.get(chave)

            if isinstance(widget, QLineEdit):
                widget.setReadOnly(False)
                widget.setVisible(True)
            elif isinstance(widget, (QDateEdit, QComboBox)):
                widget.setEnabled(True)
                widget.setVisible(True)

            if label_view is not None:
                label_view.setVisible(False)

        self.btn_salvar.setEnabled(True)

    def _on_valor_editado(self, text: str):
        from PySide6.QtWidgets import QLineEdit

        if self._formatando_valor:
            return

        edit = self.sender()
        if not isinstance(edit, QLineEdit):
            return

        valor_formatado = _formatar_texto_moeda(text)
        self._formatando_valor = True
        edit.setText(valor_formatado)
        edit.setCursorPosition(len(valor_formatado))
        self._formatando_valor = False

    def _salvar_alteracoes(self):
        if self._sistema is None:
            QMessageBox.critical(self, "Erro", "Sistema não disponível para salvar alterações.")
            return

        tipo = self.info.get("tipo")
        id_lanc = self.info.get("id")

        if id_lanc is None:
            QMessageBox.critical(self, "Erro", "ID do lançamento não encontrado.")
            return

        resp = QMessageBox.question(
            self,
            "Confirmar alterações",
            "Tem certeza que deseja salvar as alterações deste lançamento?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        # ------------ RECEITA ------------
        if tipo == "Receita":
            txt_valor = self._campos_editaveis["valor"].text().strip()
            if not txt_valor:
                QMessageBox.warning(self, "Dados incompletos", "Informe o valor.")
                return
            try:
                valor = _texto_para_float_moeda(txt_valor)
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "Valor da receita inválido.")
                return

            date_edit: QDateEdit = self._campos_editaveis["data"]
            d = date_edit.date()
            try:
                data_py = d.toPython()
            except AttributeError:
                data_py = date(d.year(), d.month(), d.day())

            combo_fp: QComboBox = self._campos_editaveis["forma_pagamento"]
            forma_enum = mapear_forma_pagamento(combo_fp.currentText())
            if forma_enum is None:
                QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
                return

            # MONTA o objeto Recebimento e envia para o backend
            rec = Recebimento(
                id=id_lanc,
                valor=valor,
                data=data_py,
                forma_pagamento=forma_enum,
                comprovante_caminho=self._caminho_imagem,
            )
            self._sistema.atualizar_recebimento(rec)

        # ------------ DESPESA ------------
        elif tipo == "Despesa":
            txt_valor = self._campos_editaveis["valor"].text().strip()
            if not txt_valor:
                QMessageBox.warning(self, "Dados incompletos", "Informe o valor.")
                return
            try:
                valor = _texto_para_float_moeda(txt_valor)
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "Valor da despesa inválido.")
                return

            desc = self._campos_editaveis["descricao"].text().strip()
            if not desc:
                QMessageBox.warning(self, "Dados incompletos", "Informe a descrição.")
                return

            date_edit: QDateEdit = self._campos_editaveis["data"]
            d = date_edit.date()
            try:
                data_lanc = d.toPython()
            except AttributeError:
                data_lanc = date(d.year(), d.month(), d.day())

            date_venc_edit: QDateEdit = self._campos_editaveis["data_vencimento"]
            dv = date_venc_edit.date()
            try:
                data_venc = dv.toPython()
            except AttributeError:
                data_venc = date(dv.year(), dv.month(), dv.day())

            combo_fp: QComboBox = self._campos_editaveis["forma_pagamento"]
            forma_enum = mapear_forma_pagamento(combo_fp.currentText())
            if forma_enum is None:
                QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
                return

            combo_tipo: QComboBox = self._campos_editaveis["tipo_conta"]
            eh_a_prazo = combo_tipo.currentText() == "Conta a prazo"
            if not eh_a_prazo:
                data_venc = None

            # MONTA o objeto Despesa e envia para o backend
            desp = Despesa(
                id=id_lanc,
                valor=valor,
                data=data_lanc,
                forma_pagamento=forma_enum,
                descricao=desc,
                eh_a_prazo=eh_a_prazo,
                data_vencimento=data_venc,
                comprovante_caminho=self._caminho_imagem,
            )
            self._sistema.atualizar_despesa(desp)

        # ------------ NOTA DE SERVIÇO ------------
        elif tipo == "Nota de serviço":
            cliente = self._campos_editaveis["cliente"].text().strip()
            if not cliente:
                QMessageBox.warning(self, "Dados incompletos", "Informe o cliente.")
                return

            desc = self._campos_editaveis["descricao"].text().strip()
            if not desc:
                QMessageBox.warning(self, "Dados incompletos", "Informe a descrição.")
                return

            txt_valor = self._campos_editaveis["valor"].text().strip()
            if not txt_valor:
                QMessageBox.warning(self, "Dados incompletos", "Informe o valor.")
                return
            try:
                valor = _texto_para_float_moeda(txt_valor)
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "Valor da nota inválido.")
                return

            date_edit: QDateEdit = self._campos_editaveis["data"]
            d = date_edit.date()
            try:
                data_os = d.toPython()
            except AttributeError:
                data_os = date(d.year(), d.month(), d.day())

            combo_sit: QComboBox = self._campos_editaveis["situacao"]
            foi_pago = combo_sit.currentText() == "Paga"

            combo_fp: QComboBox = self._campos_editaveis["forma_pagamento"]
            txt_fp = combo_fp.currentText()
            if txt_fp == "Não definido":
                forma_enum = None
            else:
                forma_enum = mapear_forma_pagamento(txt_fp)
                if forma_enum is None:
                    QMessageBox.warning(self, "Erro", "Forma de pagamento inválida.")
                    return

            # MONTA o objeto OrdemServico e envia para o backend
            os_ = OrdemServico(
                id=id_lanc,
                cliente=cliente,
                descricao=desc,
                valor_total=valor,
                data=data_os,
                foi_pago=foi_pago,
                forma_pagamento=forma_enum,
            )
            self._sistema.atualizar_ordem_servico(os_)

        else:
            # tipo desconhecido: não deveria acontecer, mas só pra garantir
            QMessageBox.warning(self, "Erro", f"Tipo de lançamento desconhecido: {tipo}")
            return

        # Depois de salvar com sucesso:
        QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")

        # volta para modo somente leitura (UI)
        self._modo_edicao = False
        self.btn_salvar.setEnabled(False)

        from PySide6.QtWidgets import QLineEdit, QDateEdit, QComboBox

        for chave, widget in self._campos_editaveis.items():
            label_view = self._labels_valores.get(chave)

            if isinstance(widget, QLineEdit):
                if label_view is not None:
                    label_view.setText(widget.text())
                widget.setReadOnly(True)
                widget.setVisible(False)

            elif isinstance(widget, QDateEdit):
                texto_data = widget.date().toString("dd/MM/yyyy")
                if label_view is not None:
                    label_view.setText(texto_data)
                widget.setEnabled(False)
                widget.setVisible(False)

            elif isinstance(widget, QComboBox):
                if label_view is not None:
                    label_view.setText(widget.currentText())
                widget.setEnabled(False)
                widget.setVisible(False)

            if label_view is not None:
                label_view.setVisible(True)


    # ============================================================
    # Imagem (seu código original)
    # ============================================================

    def _carregar_imagem(self):
        caminho = self._caminho_imagem
        if caminho and os.path.isfile(caminho):
            self.lbl_comp_path.setText(caminho)
            pix = QPixmap(caminho)
            if not pix.isNull():
                self.lbl_preview.setPixmap(pix)
                self.btn_ver_maior.setEnabled(True)
                return

        self.lbl_comp_path.setText("Nenhum comprovante ou arquivo não encontrado.")
        self.lbl_preview.setText("Sem imagem")
        self.lbl_preview.setPixmap(QPixmap())
        self.btn_ver_maior.setEnabled(False)

    def _abrir_zoom(self):
        if not (self._caminho_imagem and os.path.isfile(self._caminho_imagem)):
            return
        dlg = ImagemZoomDialog(self._caminho_imagem, self)
        dlg.exec()






# ===================== DIALOGO: RELATÓRIO DE RECEITAS =====================

class RelatorioReceitasDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)
        self.sistema = sistema

        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(950, 560)

        # dados brutos de cada linha (usado pra abrir detalhes)
        self._linhas_raw = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("Relatório de receitas")
        title.setObjectName("title")

        header_text = QVBoxLayout()
        header_text.addWidget(title)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Linha 1: período
        linha1 = QHBoxLayout()
        lbl_periodo = QLabel("Período:")
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Diário", "Semanal", "Mensal", "Tudo"])
        self.combo_periodo.setCurrentIndex(3)

        linha1.addWidget(lbl_periodo)
        linha1.addWidget(self.combo_periodo)
        linha1.addStretch()
        card_layout.addLayout(linha1)

        # Botão atualizar
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.setObjectName("secondaryButton")
        self.btn_atualizar.setFixedHeight(36)
        self.btn_atualizar.clicked.connect(self.carregar_dados)

        # Tabela – Data, Valor, Forma de pagamento
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(
            ["Data", "Valor", "Forma de pagamento"]
        )
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)

        # Duplo clique → detalhes
        self.tabela.cellDoubleClicked.connect(self._abrir_detalhes_linha)

        card_layout.addWidget(self.tabela)

        # Rodapé
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total das receitas: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        footer.addWidget(self.btn_atualizar)
        card_layout.addLayout(footer)

        root.addWidget(card)
        self.setStyleSheet(DIALOG_STYLES)

        self.carregar_dados()

    def carregar_dados(self):
        periodo = self.combo_periodo.currentText()
        limite = _limite_por_periodo(periodo)

        self._linhas_raw = []
        linhas = []
        total_receitas = 0.0

        # RECEITAS
        for r in self.sistema.listar_recebimentos():
            if limite and r.data < limite:
                continue

            data = r.data
            valor = r.valor
            forma = r.forma_pagamento.value  # ex: "pix", "dinheiro"

            # o que aparece na TABELA
            linhas.append((data, valor, forma))
            total_receitas += valor

            # dados completos p/ tela de detalhes
            self._linhas_raw.append({
                "tipo": "Receita",
                "id": r.id,
                "data": data,
                "descricao": f"Recebimento ({forma})",
                "valor": valor,
                "situacao": None,
                "forma_pagamento": forma,
                "comprovante": r.comprovante_caminho,
            })

        self.tabela.setRowCount(len(linhas))

        for row, (data, valor, forma) in enumerate(linhas):
            # Data
            data_str = _date_to_str(data)
            self.tabela.setItem(row, 0, QTableWidgetItem(data_str))

            # Valor formatado BR
            item_valor = QTableWidgetItem(
                f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.tabela.setItem(row, 1, item_valor)

            # Forma de pagamento
            self.tabela.setItem(row, 2, QTableWidgetItem(forma))

        self.lbl_total.setText(
            "Total das receitas: R$ "
            + f"{total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _abrir_detalhes_linha(self, row: int, col: int):
        if row < 0 or row >= len(self._linhas_raw):
            return

        info = self._linhas_raw[row]
        dlg = DetalheLancamentoDialog(info, self)
        dlg.exec()



# ===================== DIALOGO: RELATÓRIO DE DESPESAS =====================

class RelatorioDespesasDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)
        self.sistema = sistema

        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(950, 560)

        # dados brutos de cada linha (usado pra abrir detalhes)
        self._linhas_raw = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("Relatório de despesas")
        title.setObjectName("title")

        header_text = QVBoxLayout()
        header_text.addWidget(title)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Linha 1: período
        linha1 = QHBoxLayout()
        lbl_periodo = QLabel("Período:")
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Diário", "Semanal", "Mensal", "Tudo"])
        self.combo_periodo.setCurrentIndex(3)

        linha1.addWidget(lbl_periodo)
        linha1.addWidget(self.combo_periodo)
        linha1.addStretch()
        card_layout.addLayout(linha1)

        # Botão atualizar
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.setObjectName("secondaryButton")
        self.btn_atualizar.setFixedHeight(36)
        self.btn_atualizar.clicked.connect(self.carregar_dados)

        # Tabela – Data, Descrição, Valor, Forma de pagamento, A prazo?
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Data", "Descrição", "Valor", "Forma de pagamento", "A prazo?"]
        )
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)

        # Duplo clique → detalhes
        self.tabela.cellDoubleClicked.connect(self._abrir_detalhes_linha)

        card_layout.addWidget(self.tabela)

        # Rodapé
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total das despesas: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        footer.addWidget(self.btn_atualizar)
        card_layout.addLayout(footer)

        root.addWidget(card)
        self.setStyleSheet(DIALOG_STYLES)

        self.carregar_dados()

    def carregar_dados(self):
        periodo = self.combo_periodo.currentText()
        limite = _limite_por_periodo(periodo)

        self._linhas_raw = []
        linhas = []
        total_despesas = 0.0

        # DESPESAS
        for d in self.sistema.listar_despesas():
            if limite and d.data < limite:
                continue

            data = d.data
            descricao = d.descricao
            valor = d.valor
            forma = d.forma_pagamento.value
            prazo_str = "Sim" if d.eh_a_prazo else "Não"

            # o que vai pra TABELA
            linhas.append((data, descricao, valor, forma, prazo_str))
            total_despesas += valor

            # dados completos pro detalhe
            self._linhas_raw.append({
                "tipo": "Despesa",
                "id": d.id,
                "data": data,
                "descricao": descricao,
                "valor": valor,
                "forma_pagamento": forma,
                "eh_a_prazo": d.eh_a_prazo,
                "data_vencimento": d.data_vencimento,
                "situacao": None,
                "comprovante": d.comprovante_caminho,
            })

        self.tabela.setRowCount(len(linhas))

        for row, (data, descricao, valor, forma, prazo_str) in enumerate(linhas):
            # Data
            data_str = _date_to_str(data)
            self.tabela.setItem(row, 0, QTableWidgetItem(data_str))

            # Descrição
            self.tabela.setItem(row, 1, QTableWidgetItem(descricao))

            # Valor formatado
            item_valor = QTableWidgetItem(
                f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.tabela.setItem(row, 2, item_valor)

            # Forma
            self.tabela.setItem(row, 3, QTableWidgetItem(forma))

            # A prazo?
            self.tabela.setItem(row, 4, QTableWidgetItem(prazo_str))

        self.lbl_total.setText(
            "Total das despesas: R$ "
            + f"{total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _abrir_detalhes_linha(self, row: int, col: int):
        if row < 0 or row >= len(self._linhas_raw):
            return

        info = self._linhas_raw[row]
        dlg = DetalheLancamentoDialog(info, self)
        dlg.exec()




# ===================== DIALOGO: RELATÓRIO DE NOTAS DE SERVIÇO =====================

class RelatorioNotasDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)
        self.sistema = sistema

        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(950, 560)

        # dados brutos de cada linha (usado pra abrir detalhes)
        self._linhas_raw = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("Relatório de notas de serviço")
        title.setObjectName("title")

        header_text = QVBoxLayout()
        header_text.addWidget(title)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(btn_close)

        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Linha 1: período
        linha1 = QHBoxLayout()
        lbl_periodo = QLabel("Período:")
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Diário", "Semanal", "Mensal", "Tudo"])
        self.combo_periodo.setCurrentIndex(3)

        linha1.addWidget(lbl_periodo)
        linha1.addWidget(self.combo_periodo)
        linha1.addStretch()
        card_layout.addLayout(linha1)

        # Botão atualizar (fica no rodapé, mas criamos aqui)
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.setObjectName("secondaryButton")
        self.btn_atualizar.setFixedHeight(36)
        self.btn_atualizar.clicked.connect(self.carregar_dados)

        # Tabela – APENAS o necessário: Cliente, Valor, Pago, Data
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(
            ["Cliente", "Valor", "Pago", "Data"]
        )
        # tabela somente leitura
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)

        # Duplo clique abre a janela de detalhes (se você estiver usando DetalheLancamentoDialog)
        self.tabela.cellDoubleClicked.connect(self._abrir_detalhes_linha)

        card_layout.addWidget(self.tabela)

        # Rodapé
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Total das notas de serviço: R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        footer.addWidget(self.btn_atualizar)

        card_layout.addLayout(footer)

        root.addWidget(card)
        self.setStyleSheet(DIALOG_STYLES)

        self.carregar_dados()

    def carregar_dados(self):
        periodo = self.combo_periodo.currentText()
        limite = _limite_por_periodo(periodo)

        self._linhas_raw = []
        linhas = []
        total_notas = 0.0

        # NOTAS DE SERVIÇO
        for n in self.sistema.listar_ordens_servico():
            # filtra pelo período, se tiver limite
            if limite and n.data < limite:
                continue

            pago_int = 1 if n.foi_pago else 0
            situacao_str = "Paga" if n.foi_pago else "Não paga"
            data = n.data  # assumindo que já é date

            # o que vai para a TABELA (apenas o necessário)
            linhas.append(
                (n.cliente, n.valor_total, situacao_str, data)
            )

            total_notas += n.valor_total

            # dados completos guardados para a janela de detalhes
            self._linhas_raw.append({
                "tipo": "Nota de serviço",
                "id": n.id,
                "data": data,
                "cliente": n.cliente,
                "descricao": n.descricao,
                "valor": n.valor_total,
                "situacao": situacao_str,
                "pago_int": pago_int,
                "forma_pagamento": (
                    n.forma_pagamento.value if n.forma_pagamento is not None else "Não definido"
                ),
                "comprovante": None,
            })

        self.tabela.setRowCount(len(linhas))

        # IMPORTANTE: repare que agora eu descompacto (cliente, valor, situacao_str, data)
        for row, (cliente, valor, situacao_str, data) in enumerate(linhas):
            # Cliente
            self.tabela.setItem(row, 0, QTableWidgetItem(cliente))

            # Valor formatado BR
            item_valor = QTableWidgetItem(
                f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.tabela.setItem(row, 1, item_valor)

            # Situação: "Paga" / "Não paga"
            self.tabela.setItem(row, 2, QTableWidgetItem(situacao_str))

            # Data
            data_str = _date_to_str(data)
            self.tabela.setItem(row, 3, QTableWidgetItem(data_str))

        # total das notas
        self.lbl_total.setText(
            "Total das notas de serviço: R$ "
            + f"{total_notas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _abrir_detalhes_linha(self, row: int, col: int):
        if row < 0 or row >= len(self._linhas_raw):
            return

        info = self._linhas_raw[row]
        dlg = DetalheLancamentoDialog(info, self)
        dlg.exec()




# ===================== DIALOGO: RELATÓRIO GERAL =====================

class RelatorioGeralDialog(QDialog):
    def __init__(self, sistema: SistemaFinanceiro, parent=None):
        super().__init__(parent)
        self.sistema = sistema

        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(950, 560)

        # guarda os dados brutos de cada linha
        self._linhas_raw = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("Relatório geral")
        title.setObjectName("title")

        header_text = QVBoxLayout()
        header_text.addWidget(title)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.close)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(btn_close)

        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Linha 1: período
        linha1 = QHBoxLayout()
        lbl_periodo = QLabel("Período:")
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Diário", "Semanal", "Mensal", "Tudo"])
        self.combo_periodo.setCurrentIndex(3)

        linha1.addWidget(lbl_periodo)
        linha1.addWidget(self.combo_periodo)
        linha1.addStretch()
        card_layout.addLayout(linha1)

        # Linha 2: checkboxes de tipos
        linha2 = QHBoxLayout()
        lbl_incluir = QLabel("Incluir:")
        self.chk_receitas = QCheckBox("Receitas")
        self.chk_despesas = QCheckBox("Despesas")
        self.chk_notas = QCheckBox("Notas de serviço")

        self.chk_receitas.setChecked(True)
        self.chk_despesas.setChecked(True)
        self.chk_notas.setChecked(True)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.setObjectName("secondaryButton")
        btn_atualizar.setFixedHeight(36)
        btn_atualizar.clicked.connect(self.carregar_dados)

        linha2.addWidget(lbl_incluir)
        linha2.addWidget(self.chk_receitas)
        linha2.addWidget(self.chk_despesas)
        linha2.addWidget(self.chk_notas)
        linha2.addStretch()
        linha2.addWidget(btn_atualizar)

        card_layout.addLayout(linha2)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Tipo", "ID", "Data / Situação", "Descrição", "Valor"]
        )
        self.tabela.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)

        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Duplo clique abre a janela de detalhes
        self.tabela.cellDoubleClicked.connect(self._abrir_detalhes_linha)

        card_layout.addWidget(self.tabela)

        # Rodapé
        footer = QHBoxLayout()
        self.lbl_total = QLabel("Saldo (Receitas - Despesas): R$ 0,00")
        footer.addWidget(self.lbl_total)
        footer.addStretch()

        card_layout.addLayout(footer)

        root.addWidget(card)
        self.setStyleSheet(DIALOG_STYLES)

        self.carregar_dados()

    def carregar_dados(self):
        periodo = self.combo_periodo.currentText()
        limite = _limite_por_periodo(periodo)

        self._linhas_raw = []
        linhas = []
        total_receitas = 0.0
        total_despesas = 0.0

        # RECEITAS
        if self.chk_receitas.isChecked():
            for r in self.sistema.listar_recebimentos():
                if limite and r.data < limite:
                    continue
                linhas.append(
                    ("Receita", r.id, r.data, f"Recebimento ({r.forma_pagamento.value})", r.valor)
                )
                total_receitas += r.valor

                self._linhas_raw.append({
                    "tipo": "Receita",
                    "id": r.id,
                    "data": r.data,
                    "descricao": f"Recebimento ({r.forma_pagamento.value})",
                    "valor": r.valor,
                    "forma_pagamento": r.forma_pagamento.value,   # <--- ADICIONA ISSO
                    "comprovante": r.comprovante_caminho,
                })

        # DESPESAS
        if self.chk_despesas.isChecked():
            for d in self.sistema.listar_despesas():
                if limite and d.data < limite:
                    continue
                linhas.append(
                    ("Despesa", d.id, d.data, d.descricao, -abs(d.valor))
                )
                total_despesas += d.valor

                self._linhas_raw.append({
                    "tipo": "Despesa",
                    "id": d.id,
                    "data": d.data,
                    "descricao": d.descricao,
                    "valor": d.valor,                             # deixa positivo p/ detalhes
                    "forma_pagamento": d.forma_pagamento.value,   # <--- ADICIONA
                    "eh_a_prazo": d.eh_a_prazo,                   # <--- p/ usar no detalhe
                    "data_vencimento": d.data_vencimento,         # <--- idem
                    "comprovante": d.comprovante_caminho,
                })


        # NOTAS DE SERVIÇO
        if self.chk_notas.isChecked():
            for n in self.sistema.listar_ordens_servico():
                situacao = "Paga" if n.foi_pago else "Em aberto"
                data = getattr(n, "data", None)
                data_sit = (
                    f"{_date_to_str(data)} - {situacao}" if isinstance(data, date) else situacao
                )

                linhas.append(
                    ("Nota de serviço", n.id, data_sit, n.descricao, n.valor_total)
                )

                self._linhas_raw.append({
                    "tipo": "Nota de serviço",
                    "id": n.id,
                    "data": n.data,
                    "cliente": n.cliente,
                    "descricao": n.descricao,
                    "valor": n.valor_total,
                    "situacao": situacao,
                    "forma_pagamento": (
                        n.forma_pagamento.value if n.forma_pagamento else "Não definido"
                    ),                                             # <--- ADICIONA
                    "comprovante": None,
                })


        self.tabela.setRowCount(len(linhas))

        for row, (tipo, _id, data_ou_sit, desc, valor) in enumerate(linhas):
            item_id = QTableWidgetItem(str(_id if _id is not None else ""))
            item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)

            self.tabela.setItem(row, 0, QTableWidgetItem(tipo))
            self.tabela.setItem(row, 1, item_id)

            if isinstance(data_ou_sit, date):
                data_str = _date_to_str(data_ou_sit)
            else:
                data_str = str(data_ou_sit)

            self.tabela.setItem(row, 2, QTableWidgetItem(data_str))
            self.tabela.setItem(row, 3, QTableWidgetItem(desc))
            self.tabela.setItem(
                row,
                4,
                QTableWidgetItem(
                    f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                ),
            )

        saldo = self.sistema.calcular_saldo()
        self.lbl_total.setText(
            "Saldo (Receitas - Despesas): R$ "
            + f"{saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _abrir_detalhes_linha(self, row: int, col: int):
        if row < 0 or row >= len(self._linhas_raw):
            return

        info = self._linhas_raw[row]
        dlg = DetalheLancamentoDialog(info, self)
        dlg.exec()





# ===================== JANELA PRINCIPAL =====================

class MainWindow(QMainWindow):
    def __init__(self, sistema: SistemaFinanceiro):
        super().__init__()

        self.sistema = sistema

        self.setWindowTitle("Financeiro - Exemplo")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        lbl = QLabel("Janela principal (aqui ficaria o Financeiro)")

        # --- BOTÕES DE CADASTRO ---
        btn_nova_receita = QPushButton("+ Receita")
        btn_nova_receita.setFixedWidth(140)
        btn_nova_receita.clicked.connect(self.abrir_dialogo_receita)

        btn_nova_despesa = QPushButton("+ Despesa")
        btn_nova_despesa.setFixedWidth(140)
        btn_nova_despesa.clicked.connect(self.abrir_dialogo_despesa)

        btn_nova_nota = QPushButton("+ Nota de serviço")
        btn_nova_nota.setFixedWidth(160)
        btn_nova_nota.clicked.connect(self.abrir_dialogo_nota_servico)

        cadastro_layout = QHBoxLayout()
        cadastro_layout.setSpacing(12)
        cadastro_layout.addWidget(btn_nova_receita)
        cadastro_layout.addWidget(btn_nova_despesa)
        cadastro_layout.addWidget(btn_nova_nota)
        cadastro_layout.addStretch()

        # --- SEÇÃO RELATÓRIOS ---
        titulo_rel = QLabel("Relatórios")
        titulo_rel.setStyleSheet("font-size: 18px; font-weight: 700;")

        btn_rel_receitas = QPushButton("Relatório de receitas")
        btn_rel_receitas.clicked.connect(self.abrir_relatorio_receitas)

        btn_rel_despesas = QPushButton("Relatório de despesas")
        btn_rel_despesas.clicked.connect(self.abrir_relatorio_despesas)

        btn_rel_notas = QPushButton("Relatório de notas de serviço")
        btn_rel_notas.clicked.connect(self.abrir_relatorio_notas)

        btn_rel_geral = QPushButton("Relatório geral")
        btn_rel_geral.clicked.connect(self.abrir_relatorio_geral)

        rel_layout = QHBoxLayout()
        rel_layout.setSpacing(12)
        rel_layout.addWidget(btn_rel_receitas)
        rel_layout.addWidget(btn_rel_despesas)
        rel_layout.addWidget(btn_rel_notas)
        rel_layout.addWidget(btn_rel_geral)
        rel_layout.addStretch()

        # Monta layout principal
        layout.addWidget(lbl)
        layout.addLayout(cadastro_layout)

        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linha)

        layout.addWidget(titulo_rel)
        layout.addLayout(rel_layout)
        layout.addStretch()

        self.setCentralWidget(central)
        self.resize(1000, 650)

    # --- Abertura dos diálogos de cadastro ---
    def abrir_dialogo_receita(self):
        dialog = NovaReceitaDialog(self.sistema, self)
        dialog.exec()

    def abrir_dialogo_despesa(self):
        dialog = NovaDespesaDialog(self.sistema, self)
        dialog.exec()

    def abrir_dialogo_nota_servico(self):
        dialog = NovaNotaServicoDialog(self.sistema, self)
        dialog.exec()

    # --- Abertura dos diálogos de relatório ---
    def abrir_relatorio_receitas(self):
        dlg = RelatorioReceitasDialog(self.sistema, self)
        dlg.exec()

    def abrir_relatorio_despesas(self):
        dlg = RelatorioDespesasDialog(self.sistema, self)
        dlg.exec()

    def abrir_relatorio_notas(self):
        dlg = RelatorioNotasDialog(self.sistema, self)
        dlg.exec()

    def abrir_relatorio_geral(self):
        dlg = RelatorioGeralDialog(self.sistema, self)
        dlg.exec()


# ===================== MODO STANDALONE (opcional) =====================

def _run_standalone():
    """
    Execução direta de interface.py (modo standalone).
    Na prática, recomenda-se usar app.py como ponto de entrada,
    mas isso permite testar a interface isoladamente.
    """
    db = Database("financeiro.db")
    sistema = SistemaFinanceiro(db)

    app = QApplication(sys.argv)

    # Segoe UI como fonte padrão
    base_font = QFont("Segoe UI")
    base_font.setPointSize(10)
    app.setFont(base_font)

    window = MainWindow(sistema)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _run_standalone()