"""
Módulo de Helpers (Utilitários).

Contém funções auxiliares puras (que não dependem de estado de classe)
para formatação de texto (moeda), conversão de datas e mapeamento de enums.
Isso evita repetição de código e torna a lógica mais testável.
"""

from typing import Optional
from datetime import date, timedelta
from datetime import date, timedelta
from PySide6.QtCore import QDate, QObject, QEvent, Qt
from PySide6.QtWidgets import QLineEdit

from models import FormaPagamento

# ===================== FORMATAÇÃO E CONVERSÃO =====================

def mapear_forma_pagamento(texto: str) -> Optional[FormaPagamento]:
    """
    Converte uma string da interface (ex: 'Dinheiro', 'Pix') para o Enum FormaPagamento.
    Retorna None se não encontrar correspondência.
    """
    t = texto.strip().lower()
    mapa = {
        "dinheiro": FormaPagamento.DINHEIRO,
        "débito": FormaPagamento.DEBITO,
        "crédito": FormaPagamento.CREDITO,
        "pix": FormaPagamento.PIX,
        "boleto": FormaPagamento.BOLETO,
        "cheque": FormaPagamento.CHEQUE,
    }
    return mapa.get(t)


def _formatar_texto_moeda(texto: str) -> str:
    """
    Recebe um texto cru (ex: '1234') e formata como moeda (ex: 'R$ 12,34').
    Útil para máscaras de input enquanto o usuário digita.
    """
    # Remove tudo que não for dígito
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

    # Garante zeros à esquerda para centavos
    if len(digits) == 1:
        digits = "0" + digits

    # Separa centavos dos inteiros
    inteiros = digits[:-2]
    centavos = digits[-2:]

    if not inteiros:
        inteiros = "0"

    # Formata milhar com ponto
    inteiros_int = int(inteiros)
    inteiros_formatado = f"{inteiros_int:,}".replace(",", ".")

    return f"R$ {inteiros_formatado},{centavos}"


def _texto_para_float_moeda(texto: str) -> float:
    """
    Converte uma string formatada (ex: 'R$ 1.234,56') para float (1234.56).
    """
    txt = texto.strip()
    if txt.lower().startswith("r$"):
        txt = txt[2:].strip()
    
    # Remove pontuação de milhar e troca vírgula decimal por ponto
    normalizado = txt.replace(".", "").replace(",", ".")
    return float(normalizado)


def qdate_to_date(qd: QDate) -> date:
    """
    Converte um objeto QDate (PySide) para datetime.date (Python nativo) de forma segura.
    Necessário porque as versões do Qt podem variar métodos como toPython().
    """
    try:
        return qd.toPython()
    except AttributeError:
        return date(qd.year(), qd.month(), qd.day())


def _date_to_str(d: Optional[date]) -> str:
    """Formata data para string BR (dd/mm/aaaa)."""
    if not d:
        return ""
    return d.strftime("%d/%m/%Y")


def _bool_to_str(b: bool) -> str:
    """Converte booleano para 'Sim'/'Não'."""
    return "Sim" if b else "Não"


def _limite_por_periodo(nome: str) -> Optional[date]:
    """
    Calcula a data de corte com base no filtro selecionado (Diário, Semanal, etc).
    Retorna None se for 'Tudo' (sem limite).
    """
    hoje = date.today()
    nome = nome.lower()

    if "diário" in nome or "diario" in nome:
        return hoje
    if "semanal" in nome:
        # Últimos 7 dias (contando hoje)
        return hoje - timedelta(days=6)
    if "mensal" in nome:
        # Últimos 30 dias
        return hoje - timedelta(days=29)
    
    # "Tudo" ou não reconhecido
    return None


def calcular_range_dia(data: date) -> tuple[date, date]:
    """
    Retorna a faixa de datas para um único dia.
    
    Args:
        data: A data específica
        
    Returns:
        Tupla (data_inicio, data_fim) onde ambas são iguais
    """
    return (data, data)


def calcular_range_mes(ano: int, mes: int) -> tuple[date, date]:
    """
    Retorna a faixa de datas para um mês inteiro.
    
    Args:
        ano: Ano (ex: 2026)
        mes: Mês (1-12)
        
    Returns:
        Tupla (primeiro_dia_mes, ultimo_dia_mes)
    """
    from calendar import monthrange
    
    inicio = date(ano, mes, 1)
    ultimo_dia = monthrange(ano, mes)[1]
    fim = date(ano, mes, ultimo_dia)
    
    return (inicio, fim)


def calcular_range_ano(ano: int) -> tuple[date, date]:
    """
    Retorna a faixa de datas para um ano inteiro.
    
    Args:
        ano: Ano (ex: 2026)
        
    Returns:
        Tupla (01/01/ano, 31/12/ano)
    """
    inicio = date(ano, 1, 1)
    fim = date(ano, 12, 31)
    
    return (inicio, fim)


# ===================== FILTROS DE EVENTOS (UI) =====================

class EnterKeyFilter(QObject):
    """
    Filtro de evento para interceptar a tecla Enter em campos de entrada.
    
    Quando Enter é pressionado em um QLineEdit, move o foco para o próximo
    widget na cadeia de foco, em vez de fechar/submeter o diálogo.
    """
    
    def eventFilter(self, obj, event):
        """
        Intercepta eventos de teclado.
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
