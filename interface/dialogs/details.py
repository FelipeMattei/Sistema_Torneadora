"""
Módulo de Detalhes (Details).

Contém os diálogos responsáveis por exibir os detalhes completos de um lançamento
(Receita, Despesa ou OS) e permitir a visualização de comprovantes com zoom.
"""

import os
from datetime import date
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QGraphicsView, QGraphicsScene, QScrollArea, QWidget, QMessageBox,
    QLineEdit, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QPainter

from models import Recebimento, Despesa, OrdemServico, FormaPagamento
from interface.styles import DIALOG_STYLES
from interface.helpers import (
    mapear_forma_pagamento, 
    _formatar_texto_moeda, 
    _texto_para_float_moeda, 
    _date_to_str
)

# ===================== ZOOM DE IMAGEM (Comprovante) =====================

class ZoomGraphicsView(QGraphicsView):
    """
    Componente visual que permite dar zoom em uma imagem usando o scroll do mouse
    e arrastar a imagem com o clique (Pan).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # Renderização suave para melhor qualidade
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    def wheelEvent(self, event):
        """Captura o evento de rolagem do mouse para aplicar zoom."""
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        self.scale(factor, factor)


class ImagemZoomDialog(QDialog):
    """
    Janela dedicada para visualizar o comprovante em tela cheia.
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

        # Abre já maximizado para melhor visualização
        self.setWindowState(Qt.WindowMaximized)


# ===================== DIÁLOGO DE DETALHES =====================

class DetalheLancamentoDialog(QDialog):
    """
    Janela que exibe todas as informações de um item (Receita, Despesa, OS).
    Permite:
    1. Visualizar dados (somente leitura inicialmente)
    2. Ver comprovante (com preview e botão de zoom)
    3. Editar dados (botão 'Editar' libera os campos)
    """

    def __init__(self, info: Dict, parent=None):
        super().__init__(parent)

        self.info = info
        self._caminho_imagem = info.get("comprovante")
        # Mantém referência ao sistema para poder salvar edições
        self._sistema = getattr(parent, "sistema", None)

        # Controle de campos editáveis (chave -> widget)
        self._campos_editaveis: Dict[str, QWidget] = {}
        # Controle de labels de visualização (chave -> label)
        self._labels_valores: Dict[str, QLabel] = {}

        self._modo_edicao = False
        self._formatando_valor = False

        # Configuração visual (sem bordas do sistema operacional)
        self.setObjectName("relatorioGeralDialog")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLES)
        self.resize(720, 550)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(12)

        # --- Cabeçalho ---
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

        # --- Dados Principais ---
        tipo = self.info.get("tipo", "-")
        self._add_label_simples(card_layout, "Tipo", tipo)
        self._add_label_simples(card_layout, "ID", self.info.get("id", "-"))

        # Monta os campos específicos dependendo do tipo de dado
        if tipo == "Nota de serviço":
            self._montar_campos_nota_servico(card_layout, self.info)
        elif tipo == "Receita":
            self._montar_campos_receita(card_layout, self.info)
        elif tipo == "Despesa":
            self._montar_campos_despesa(card_layout, self.info)
        else:
            self._montar_campos_genericos(card_layout, self.info)

        # --- Seção de Comprovante ---
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

        # Nota de serviço não costuma ter comprovante salvo, então ocultamos
        if tipo == "Nota de serviço":
            self.comp_frame.setVisible(False)
        else:
            self._carregar_imagem()

        # --- Rodapé (Botões) ---
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
        self.btn_salvar.setEnabled(False) # Habilitado só no modo edição
        row_btn.addWidget(self.btn_salvar)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("secondaryButton")
        btn_fechar.setFixedHeight(42)
        btn_fechar.clicked.connect(self.reject)
        row_btn.addWidget(btn_fechar)

        card_layout.addLayout(row_btn)
        root.addWidget(card)

    # ================= HELPERS DE UI =================

    def _add_label_simples(self, layout, titulo, valor):
        """Adiciona apenas uma label de texto (não editável)."""
        lbl = QLabel(f"{titulo}: {valor}")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

    def _add_input_linha(self, layout, titulo, chave, valor_inicial, is_valor=False):
        """
        Cria um par Label (leitura) + Input (edição) para um campo de texto.
        O Input começa oculto.
        """
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 0)
        lbl_titulo = QLabel(f"{titulo}:")
        lbl_valor = QLabel(str(valor_inicial))
        
        edit = QLineEdit()
        edit.setText(str(valor_inicial))
        edit.setReadOnly(True)
        edit.setVisible(False)

        if is_valor:
            edit.setPlaceholderText("R$ 0,00")
            edit.textEdited.connect(self._on_valor_editado)

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(edit, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = edit
        self._labels_valores[chave] = lbl_valor

    def _add_data_linha(self, layout, titulo, chave, data_inicial):
        """Cria par Label + DateEdit para campos de data."""
        row = QHBoxLayout()
        lbl_titulo = QLabel(f"{titulo}:")
        
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        
        if isinstance(data_inicial, date):
            qd = QDate(data_inicial.year, data_inicial.month, data_inicial.day)
        else:
            qd = QDate.currentDate()
            
        date_edit.setDate(qd)
        date_edit.setEnabled(False)
        date_edit.setVisible(False)

        lbl_valor = QLabel(qd.toString("dd/MM/yyyy"))

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(date_edit, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = date_edit
        self._labels_valores[chave] = lbl_valor

    def _add_combo_linha(self, layout, titulo, chave, opcoes, valor_atual):
        """Cria par Label + ComboBox para seleção."""
        row = QHBoxLayout()
        lbl_titulo = QLabel(f"{titulo}:")
        
        combo = QComboBox()
        combo.addItems(opcoes)
        
        # Seleciona o valor atual se existir na lista
        if valor_atual is not None:
            idx = combo.findText(str(valor_atual), Qt.MatchFixedString)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        
        combo.setEnabled(False)
        combo.setVisible(False)
        
        texto_inicial = combo.currentText() if combo.currentIndex() >= 0 else "-"
        lbl_valor = QLabel(texto_inicial)

        row.addWidget(lbl_titulo)
        row.addWidget(lbl_valor, 1)
        row.addWidget(combo, 1)
        layout.addLayout(row)

        self._campos_editaveis[chave] = combo
        self._labels_valores[chave] = lbl_valor

    # ================= MÉTODOS DE MONTAGEM =================

    def _montar_campos_receita(self, layout, info):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        forma = info.get("forma_pagamento", "Não definido")

        # Valor
        valor_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)
        
        # Data
        self._add_data_linha(layout, "Data", "data", data)
        
        # Forma Pagamento
        opcoes_fp = ["Dinheiro", "Debito", "Credito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)

    def _montar_campos_despesa(self, layout, info):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        forma = info.get("forma_pagamento", "Não definido")
        descricao = info.get("descricao", "-")
        eh_a_prazo = bool(info.get("eh_a_prazo", False))
        data_venc = info.get("data_vencimento")

        valor_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)
        self._add_data_linha(layout, "Data de lançamento", "data", data)
        
        opcoes_fp = ["Dinheiro", "Debito", "Credito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)
        
        self._add_input_linha(layout, "Descrição", "descricao", descricao)

        opcoes_conta = ["Conta à vista", "Conta a prazo"]
        atual = "Conta a prazo" if eh_a_prazo else "Conta à vista"
        self._add_combo_linha(layout, "Tipo de conta", "tipo_conta", opcoes_conta, atual)
        
        self._add_data_linha(layout, "Data de vencimento", "data_vencimento", data_venc)

    def _montar_campos_nota_servico(self, layout, info):
        data = info.get("data")
        valor = abs(info.get("valor", 0.0))
        cliente = info.get("cliente", "-")
        descricao = info.get("descricao", "-")
        situacao = info.get("situacao", "Não paga")
        forma = info.get("forma_pagamento", "Não definido")

        self._add_input_linha(layout, "Cliente", "cliente", cliente)
        self._add_input_linha(layout, "Descrição do serviço", "descricao", descricao)
        
        valor_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self._add_input_linha(layout, "Valor", "valor", valor_str, is_valor=True)
        
        self._add_data_linha(layout, "Data", "data", data)
        
        opcoes_sit = ["Paga", "Não paga"]
        self._add_combo_linha(layout, "Situação", "situacao", opcoes_sit, situacao)
        
        opcoes_fp = ["Não definido", "Dinheiro", "Debito", "Credito", "PIX", "Boleto", "Cheque"]
        self._add_combo_linha(layout, "Forma de pagamento", "forma_pagamento", opcoes_fp, forma)

    def _montar_campos_genericos(self, layout, info):
        """Fallback para tipos desconhecidos."""
        self._add_label_simples(layout, "Descrição", info.get("descricao", "-"))
        valor = info.get("valor", 0.0)
        self._add_label_simples(layout, "Valor", f"R$ {valor:.2f}")

    # ================= LÓGICA DE COMPROVANTE =================

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

    # ================= LÓGICA DE EDIÇÃO =================

    def _ativar_edicao(self):
        """Alterna a interface para o modo de edição."""
        if self._modo_edicao:
            return

        self._modo_edicao = True
        
        # Mostra widgets de edição e esconde labels
        for chave, widget in self._campos_editaveis.items():
            label_view = self._labels_valores.get(chave)
            
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(False)
                widget.setVisible(True)
            elif isinstance(widget, (QDateEdit, QComboBox)):
                widget.setEnabled(True)
                widget.setVisible(True)
            
            if label_view:
                label_view.setVisible(False)

        self.btn_salvar.setEnabled(True)

    def _on_valor_editado(self, text: str):
        """Aplica máscara de moeda enquanto edita."""
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
        """Coleta os dados editados e chama o serviço de atualização."""
        if self._sistema is None:
            QMessageBox.critical(self, "Erro", "Sistema não disponível para salvar alterações.")
            return

        tipo = self.info.get("tipo")
        id_lanc = self.info.get("id")

        if id_lanc is None:
            QMessageBox.critical(self, "Erro", "ID do lançamento não encontrado.")
            return

        # Confirmação
        resp = QMessageBox.question(
            self,
            "Confirmar alterações",
            "Tem certeza que deseja salvar as alterações deste lançamento?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            if tipo == "Receita":
                self._salvar_receita(id_lanc)
            elif tipo == "Despesa":
                self._salvar_despesa(id_lanc)
            elif tipo == "Nota de serviço":
                self._salvar_nota(id_lanc)
            else:
                QMessageBox.warning(self, "Erro", f"Tipo desconhecido: {tipo}")
                return
        except ValueError as e:
            QMessageBox.warning(self, "Erro de Validação", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao salvar:\n{e}")
            return

        # Se chegou aqui, deu certo
        QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")
        
        # Reseta UI para modo leitura
        self._modo_edicao = False
        self.btn_salvar.setEnabled(False)
        self._atualizar_labels_pos_salvamento()

    def _atualizar_labels_pos_salvamento(self):
        """Copia os valores dos widgets de volta para as labels e restaura modo leitura."""
        for chave, widget in self._campos_editaveis.items():
            label_view = self._labels_valores.get(chave)
            
            # Atualiza texto da label e esconde widget
            if isinstance(widget, QLineEdit):
                if label_view: label_view.setText(widget.text())
                widget.setReadOnly(True)
                widget.setVisible(False)
            elif isinstance(widget, QDateEdit):
                if label_view: label_view.setText(widget.date().toString("dd/MM/yyyy"))
                widget.setEnabled(False)
                widget.setVisible(False)
            elif isinstance(widget, QComboBox):
                if label_view: label_view.setText(widget.currentText())
                widget.setEnabled(False)
                widget.setVisible(False)
            
            if label_view:
                label_view.setVisible(True)

    # Lógicas específicas de salvamento para cada tipo

    def _salvar_receita(self, id_lanc):
        txt_valor = self._campos_editaveis["valor"].text()
        valor = _texto_para_float_moeda(txt_valor)
        if valor <= 0: raise ValueError("O valor deve ser maior que zero.")

        d = self._campos_editaveis["data"].date()
        # Tratamento seguro de data para Python < 3.8 se necessário, ou PySide antigo
        try: data_py = d.toPython()
        except AttributeError: data_py = date(d.year(), d.month(), d.day())

        forma_text = self._campos_editaveis["forma_pagamento"].currentText()
        forma_enum = mapear_forma_pagamento(forma_text)
        if not forma_enum: raise ValueError("Forma de pagamento inválida.")

        rec = Recebimento(
            id=id_lanc,
            valor=valor,
            data=data_py,
            forma_pagamento=forma_enum,
            comprovante_caminho=self._caminho_imagem
        )
        self._sistema.atualizar_recebimento(rec)

    def _salvar_despesa(self, id_lanc):
        txt_valor = self._campos_editaveis["valor"].text()
        valor = _texto_para_float_moeda(txt_valor)
        
        desc = self._campos_editaveis["descricao"].text().strip()
        if not desc: raise ValueError("A descrição é obrigatória.")

        d = self._campos_editaveis["data"].date()
        try: data_lanc = d.toPython()
        except AttributeError: data_lanc = date(d.year(), d.month(), d.day())

        forma_text = self._campos_editaveis["forma_pagamento"].currentText()
        forma_enum = mapear_forma_pagamento(forma_text)
        
        tipo_conta = self._campos_editaveis["tipo_conta"].currentText()
        eh_a_prazo = (tipo_conta == "Conta a prazo")
        
        data_venc = None
        if eh_a_prazo:
            dv = self._campos_editaveis["data_vencimento"].date()
            try: data_venc = dv.toPython()
            except AttributeError: data_venc = date(dv.year(), dv.month(), dv.day())

        desp = Despesa(
            id=id_lanc,
            valor=valor,
            data=data_lanc,
            forma_pagamento=forma_enum,
            descricao=desc,
            eh_a_prazo=eh_a_prazo,
            data_vencimento=data_venc,
            comprovante_caminho=self._caminho_imagem
        )
        self._sistema.atualizar_despesa(desp)

    def _salvar_nota(self, id_lanc):
        cliente = self._campos_editaveis["cliente"].text().strip()
        desc = self._campos_editaveis["descricao"].text().strip()
        if not cliente: raise ValueError("Cliente obrigatório.")
        if not desc: raise ValueError("Descrição obrigatória.")

        txt_valor = self._campos_editaveis["valor"].text()
        valor = _texto_para_float_moeda(txt_valor)

        d = self._campos_editaveis["data"].date()
        try: data_os = d.toPython()
        except AttributeError: data_os = date(d.year(), d.month(), d.day())

        foi_pago = (self._campos_editaveis["situacao"].currentText() == "Paga")
        
        forma_text = self._campos_editaveis["forma_pagamento"].currentText()
        forma_enum = None
        if forma_text != "Não definido":
            forma_enum = mapear_forma_pagamento(forma_text)

        os_ = OrdemServico(
            id=id_lanc,
            cliente=cliente,
            descricao=desc,
            valor_total=valor,
            data=data_os,
            foi_pago=foi_pago,
            forma_pagamento=forma_enum
        )
        self._sistema.atualizar_ordem_servico(os_)

