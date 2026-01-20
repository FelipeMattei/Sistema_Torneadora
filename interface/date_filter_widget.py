"""
Módulo do Widget de Filtro de Data.

Fornece um widget reutilizável para filtrar dados por dia, mês ou ano específicos.
O usuário pode escolher o modo de filtro e selecionar a data apropriada.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date
from typing import Tuple
from PySide6.QtCore import QLocale


class DateFilterWidget(QWidget):
    """
    Widget de filtro de data com três modos: Dia, Mês e Ano.
    
    Emite o sinal filterChanged quando o usuário altera o filtro.
    """
    
    filterChanged = Signal()  # Sinal emitido quando o filtro muda
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Label
        layout.addWidget(QLabel("Filtrar por:"))
        
        # Modo de filtro (Dia, Mês, Ano)
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["Dia", "Mês", "Ano", "Tudo"])
        self.combo_modo.setFixedHeight(36)
        self.combo_modo.currentIndexChanged.connect(self._on_modo_changed)
        layout.addWidget(self.combo_modo)
        
        # Seletor de data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(36)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.date_edit.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        layout.addWidget(self.date_edit)
        
        # Label de informação sobre o filtro atual
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_info)
        
        layout.addStretch()
        
        # Inicializa com modo "Tudo"
        self.combo_modo.setCurrentIndex(3)
        self._on_modo_changed()
        
    def _on_modo_changed(self):
        """Atualiza a interface quando o modo de filtro muda."""
        modo = self.combo_modo.currentText()
        
        if modo == "Dia":
            self.date_edit.setDisplayFormat("dd/MM/yyyy")
            self.date_edit.setEnabled(True)
            self._update_info_label()
        elif modo == "Mês":
            self.date_edit.setDisplayFormat("MMMM yyyy")
            self.date_edit.setEnabled(True)
            self._update_info_label()
        elif modo == "Ano":
            self.date_edit.setDisplayFormat("yyyy")
            self.date_edit.setEnabled(True)
            self._update_info_label()
        else:  # Tudo
            self.date_edit.setEnabled(False)
            self.lbl_info.setText("Mostrando todos os registros")
        
        self.filterChanged.emit()
    
    def _on_date_changed(self):
        """Atualiza quando a data selecionada muda."""
        self._update_info_label()
        self.filterChanged.emit()
    
    def _update_info_label(self):
        """Atualiza o label de informação baseado no filtro atual."""
        modo = self.combo_modo.currentText()
        qd = self.date_edit.date()
        
        if modo == "Dia":
            self.lbl_info.setText(f"Exato: {qd.day():02d}/{qd.month():02d}/{qd.year()}")
        elif modo == "Mês":
            mes_nome = QLocale(QLocale.Portuguese, QLocale.Brazil).toString(qd, "MMMM yyyy")
            self.lbl_info.setText(f"Todo o mês: {mes_nome}")
        elif modo == "Ano":
            self.lbl_info.setText(f"Todo o ano: {qd.year()}")
    
    def get_date_range(self) -> Tuple[date | None, date | None]:
        """
        Retorna a faixa de datas (inicio, fim) baseada no filtro atual.
        
        Returns:
            (None, None) se modo "Tudo"
            (data_inicio, data_fim) para os outros modos
        """
        modo = self.combo_modo.currentText()
        
        if modo == "Tudo":
            return (None, None)
        
        qd = self.date_edit.date()
        year = qd.year()
        month = qd.month()
        day = qd.day()
        
        if modo == "Dia":
            # Mesmo dia, início e fim
            dt = date(year, month, day)
            return (dt, dt)
        
        elif modo == "Mês":
            # Primeiro e último dia do mês
            inicio = date(year, month, 1)
            # Encontra o último dia do mês
            if month == 12:
                fim = date(year, 12, 31)
            else:
                from calendar import monthrange
                ultimo_dia = monthrange(year, month)[1]
                fim = date(year, month, ultimo_dia)
            return (inicio, fim)
        
        elif modo == "Ano":
            # Primeiro e último dia do ano
            inicio = date(year, 1, 1)
            fim = date(year, 12, 31)
            return (inicio, fim)
        
        return (None, None)
    
    def get_modo_texto(self) -> str:
        """Retorna o texto descritivo do modo atual."""
        return self.combo_modo.currentText()

    def set_modo(self, modo_texto: str, data_ref: date = None):
        """
        Define programaticamente o modo de filtro e a data.
        
        Args:
            modo_texto: "Dia", "Mês", "Ano" ou "Tudo"
            data_ref: Data para setar no date_edit. Se None, usa data atual.
        """
        index = self.combo_modo.findText(modo_texto)
        if index >= 0:
            self.combo_modo.setCurrentIndex(index)
        
        if data_ref:
            self.date_edit.setDate(data_ref)
        elif modo_texto != "Tudo":
            self.date_edit.setDate(QDate.currentDate())
        
        # Força atualização
        self._on_modo_changed()
