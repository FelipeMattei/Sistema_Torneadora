"""
Diálogo para adicionar ou editar funcionários.
"""

from datetime import date
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QDateEdit, QSpinBox,
    QMessageBox, QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QDate, QObject, QEvent
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from models import Funcionario
from interface.styles import DIALOG_STYLES
from interface.helpers import EnterKeyFilter


def pydate_to_qdate(d: Optional[date]) -> QDate:
    if not d:
        return QDate.currentDate()
    return QDate(d.year, d.month, d.day)


def qdate_to_pydate(qd: QDate) -> date:
    return date(qd.year(), qd.month(), qd.day())


class NoWheelFilter(QObject):
    """Impede que o scroll do mouse altere valores/opções em ComboBox/SpinBox/DateEdit."""
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            # Bloqueia para não mudar opções com a roda do mouse
            return True
        return super().eventFilter(obj, event)


class AddEditEmployeeDialog(QDialog):
    def __init__(self, sistema, parent=None, funcionario: Optional[Funcionario] = None):
        super().__init__(parent)
        self.sistema = sistema
        self.funcionario_atual = funcionario
        self.foto_caminho = funcionario.foto_caminho if funcionario else None

        self.setObjectName("addEditEmployeeDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(DIALOG_STYLES)

        self.setWindowTitle("Novo Funcionário" if not funcionario else "Editar Funcionário")
        self.resize(640, 720)

        self.enter_filter = EnterKeyFilter(self)
        self.no_wheel_filter = NoWheelFilter(self)

        self._setup_ui()

        if funcionario:
            self._carregar_dados()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        header_titles = QVBoxLayout()

        titulo_texto = "Cadastro de Funcionário" if not self.funcionario_atual else "Editar Funcionário"
        header_titles.addWidget(QLabel(titulo_texto, objectName="title"))
        header_titles.addWidget(QLabel("Preencha os dados abaixo.", objectName="subtitle"))

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeButton")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.reject)

        header.addLayout(header_titles)
        header.addStretch()
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # Linha
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(line)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        # Transparente para mostrar o cinza do card
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        scroll.viewport().setStyleSheet("background: transparent;")

        content_widget = QWidget()

        # ✅ FIX PRINCIPAL:
        # Em alguns casos o QScrollArea faz os filhos não herdarem o QSS do diálogo.
        # Reaplicamos o mesmo stylesheet dentro do conteúdo scrollável.
        content_widget.setAttribute(Qt.WA_StyledBackground, True)
        content_widget.setStyleSheet(DIALOG_STYLES)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 12, 0)
        content_layout.setSpacing(12)

        scroll.setWidget(content_widget)
        card_layout.addWidget(scroll)

        # Conteúdo
        content_layout.addWidget(QLabel("Dados pessoais", objectName="sectionTitle"))

        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Nome Completo")
        self.txt_nome.setFixedHeight(44)
        self.txt_nome.installEventFilter(self.enter_filter)
        content_layout.addWidget(self.txt_nome)

        row_cpf_tel = QHBoxLayout()
        row_cpf_tel.setSpacing(10)

        self.txt_cpf = QLineEdit()
        self.txt_cpf.setPlaceholderText("CPF (000.000.000-00)")
        self.txt_cpf.setMaxLength(14)
        self.txt_cpf.setFixedHeight(44)
        self.txt_cpf.installEventFilter(self.enter_filter)

        self.txt_telefone = QLineEdit()
        self.txt_telefone.setPlaceholderText("Telefone")
        self.txt_telefone.setFixedHeight(44)
        self.txt_telefone.installEventFilter(self.enter_filter)

        row_cpf_tel.addWidget(self.txt_cpf)
        row_cpf_tel.addWidget(self.txt_telefone)
        content_layout.addLayout(row_cpf_tel)

        content_layout.addWidget(QLabel("Dados contratuais", objectName="sectionTitle"))

        self.txt_cargo = QLineEdit()
        self.txt_cargo.setPlaceholderText("Cargo / Função")
        self.txt_cargo.setFixedHeight(44)
        self.txt_cargo.installEventFilter(self.enter_filter)
        content_layout.addWidget(self.txt_cargo)

        row_dates = QHBoxLayout()
        row_dates.setSpacing(10)

        col_adm = QVBoxLayout()
        col_adm.setSpacing(6)
        col_adm.addWidget(QLabel("Admissão", objectName="sectionTitle"))

        self.date_admissao = QDateEdit()
        self.date_admissao.setCalendarPopup(True)
        self.date_admissao.setDisplayFormat("dd/MM/yyyy")
        self.date_admissao.setDate(QDate.currentDate())
        self.date_admissao.setFixedHeight(44)
        self.date_admissao.installEventFilter(self.no_wheel_filter)
        col_adm.addWidget(self.date_admissao)

        col_pag = QVBoxLayout()
        col_pag.setSpacing(6)
        col_pag.addWidget(QLabel("Dia de pagamento", objectName="sectionTitle"))

        self.spin_dia_pagamento = QSpinBox()
        self.spin_dia_pagamento.setRange(1, 31)
        self.spin_dia_pagamento.setValue(5)
        self.spin_dia_pagamento.setFixedHeight(44)
        self.spin_dia_pagamento.installEventFilter(self.no_wheel_filter)
        col_pag.addWidget(self.spin_dia_pagamento)

        row_dates.addLayout(col_adm)
        row_dates.addLayout(col_pag)
        content_layout.addLayout(row_dates)

        content_layout.addWidget(QLabel("Controle / benefícios", objectName="sectionTitle"))

        row_benefits = QHBoxLayout()
        row_benefits.setSpacing(10)

        col_13 = QVBoxLayout()
        col_13.setSpacing(6)
        col_13.addWidget(QLabel("Mês do 13º salário", objectName="sectionTitle"))
        self.combo_mes_13 = self._criar_combo_meses()
        self.combo_mes_13.setFixedHeight(44)
        self.combo_mes_13.installEventFilter(self.no_wheel_filter)
        col_13.addWidget(self.combo_mes_13)

        col_ferias = QVBoxLayout()
        col_ferias.setSpacing(6)
        col_ferias.addWidget(QLabel("Mês de férias", objectName="sectionTitle"))
        self.combo_mes_ferias = self._criar_combo_meses()
        self.combo_mes_ferias.setFixedHeight(44)
        self.combo_mes_ferias.installEventFilter(self.no_wheel_filter)
        col_ferias.addWidget(self.combo_mes_ferias)

        row_benefits.addLayout(col_13)
        row_benefits.addLayout(col_ferias)
        content_layout.addLayout(row_benefits)

        if self.funcionario_atual:
            content_layout.addWidget(QLabel("Data demissão (opcional)", objectName="sectionTitle"))
            self.date_demissao = QDateEdit()
            self.date_demissao.setCalendarPopup(True)
            self.date_demissao.setDisplayFormat("dd/MM/yyyy")
            self.date_demissao.setFixedHeight(44)
            self.date_demissao.installEventFilter(self.no_wheel_filter)
            self.date_demissao.setDate(QDate.currentDate())
            content_layout.addWidget(self.date_demissao)

        content_layout.addWidget(QLabel("Foto do funcionário", objectName="sectionTitle"))

        row_foto = QHBoxLayout()
        row_foto.setSpacing(12)

        self.lbl_foto_preview = QLabel()
        self.lbl_foto_preview.setFixedSize(80, 80)
        self.lbl_foto_preview.setAlignment(Qt.AlignCenter)
        self.lbl_foto_preview.setStyleSheet(
            "background-color: #ddd; border-radius: 40px; border: 2px solid white;"
        )

        btn_foto = QPushButton("Selecionar foto")
        btn_foto.setObjectName("fileButton")
        btn_foto.setFixedSize(150, 44)
        btn_foto.clicked.connect(self._selecionar_foto)

        row_foto.addWidget(self.lbl_foto_preview)
        row_foto.addWidget(btn_foto)
        row_foto.addStretch()
        content_layout.addLayout(row_foto)

        content_layout.addStretch(1)

        # Footer
        card_layout.addSpacing(8)
        row_btns = QHBoxLayout()
        row_btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setFixedHeight(46)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar funcionário" if not self.funcionario_atual else "Salvar alterações")
        btn_salvar.setObjectName("primaryButton")
        btn_salvar.setFixedHeight(46)
        btn_salvar.clicked.connect(self._salvar)

        row_btns.addWidget(btn_cancelar)
        row_btns.addWidget(btn_salvar)
        card_layout.addLayout(row_btns)

        root.addWidget(card)
        self._atualizar_preview_foto()

    def _criar_combo_meses(self) -> QComboBox:
        cb = QComboBox()
        cb.addItem("Não definido", None)
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        for i, m in enumerate(meses, start=1):
            cb.addItem(m, i)
        return cb

    def _selecionar_foto(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.foto_caminho = path
            self._atualizar_preview_foto()

    def _atualizar_preview_foto(self):
        if not self.foto_caminho:
            self.lbl_foto_preview.setText("Foto")
            self.lbl_foto_preview.setPixmap(QPixmap())
            return

        pix = QPixmap(self.foto_caminho)
        if pix.isNull():
            self.lbl_foto_preview.setText("X")
            self.lbl_foto_preview.setPixmap(QPixmap())
            return

        size = 80
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)

        scaled_pix = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (scaled_pix.width() - size) // 2
        y = (scaled_pix.height() - size) // 2
        cropped = scaled_pix.copy(x, y, size, size)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, cropped)
        painter.end()

        self.lbl_foto_preview.setPixmap(rounded)
        self.lbl_foto_preview.setText("")

    def _carregar_dados(self):
        f = self.funcionario_atual
        self.txt_nome.setText(getattr(f, "nome", "") or "")
        self.txt_cpf.setText(getattr(f, "cpf", "") or "")
        self.txt_telefone.setText(getattr(f, "telefone", "") or "")
        self.txt_cargo.setText(getattr(f, "cargo", "") or "")

        self.date_admissao.setDate(pydate_to_qdate(getattr(f, "data_admissao", None)))

        dia_pag = getattr(f, "dia_pagamento", None)
        if dia_pag:
            self.spin_dia_pagamento.setValue(int(dia_pag))

        mes13 = getattr(f, "mes_decimo_terceiro", None)
        if mes13:
            self.combo_mes_13.setCurrentIndex(int(mes13))

        mesfer = getattr(f, "mes_ferias", None)
        if mesfer:
            self.combo_mes_ferias.setCurrentIndex(int(mesfer))

        if hasattr(self, "date_demissao"):
            dt_dem = getattr(f, "data_demissao", None)
            if dt_dem:
                self.date_demissao.setDate(pydate_to_qdate(dt_dem))
            else:
                self.date_demissao.setDate(QDate.currentDate())

        self.foto_caminho = getattr(f, "foto_caminho", None)
        self._atualizar_preview_foto()

    def _salvar(self):
        nome = self.txt_nome.text().strip()
        cpf = self.txt_cpf.text().strip()

        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome é obrigatório.")
            return
        if not cpf:
            QMessageBox.warning(self, "Aviso", "O CPF é obrigatório.")
            return

        telefone = self.txt_telefone.text().strip()
        cargo = self.txt_cargo.text().strip()
        dt_admissao = qdate_to_pydate(self.date_admissao.date())
        dia_pag = int(self.spin_dia_pagamento.value())

        mes_13 = self.combo_mes_13.currentData()
        mes_ferias = self.combo_mes_ferias.currentData()

        dt_demissao = None
        if hasattr(self, "date_demissao"):
            qd = self.date_demissao.date()
            tinha_demissao = bool(getattr(self.funcionario_atual, "data_demissao", None)) if self.funcionario_atual else False
            if tinha_demissao:
                dt_demissao = qdate_to_pydate(qd)
            else:
                if qd != QDate.currentDate():
                    dt_demissao = qdate_to_pydate(qd)

        try:
            if self.funcionario_atual:
                f = self.funcionario_atual
                f.nome = nome
                f.cpf = cpf
                f.telefone = telefone
                f.cargo = cargo
                f.foto_caminho = self.foto_caminho
                f.data_admissao = dt_admissao
                f.dia_pagamento = dia_pag
                f.mes_decimo_terceiro = mes_13
                f.mes_ferias = mes_ferias
                f.data_demissao = dt_demissao

                self.sistema.atualizar_funcionario(f)
                QMessageBox.information(self, "Sucesso", "Funcionário atualizado com sucesso!")
            else:
                self.sistema.registrar_funcionario(
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    cargo=cargo,
                    data_admissao=dt_admissao,
                    dia_pagamento=dia_pag,
                    foto_caminho=self.foto_caminho,
                    mes_decimo_terceiro=mes_13,
                    mes_ferias=mes_ferias
                )
                QMessageBox.information(self, "Sucesso", "Funcionário cadastrado com sucesso!")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")
