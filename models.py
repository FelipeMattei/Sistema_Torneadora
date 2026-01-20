"""
Módulo de modelos de domínio.

Contém as classes que representam os objetos principais do sistema,
como Recebimento, Despesa, OrdemServico e FormaPagamento. Aqui ficam
apenas as estruturas de dados (atributos) e, se necessário, métodos
simples relacionados a esses objetos, sem acesso direto ao banco
nem à interface gráfica.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

class FormaPagamento(Enum):
    """Enumeração das formas de pagamento suportadas no sistema."""
    DINHEIRO = "Dinheiro"
    PIX = "Pix"
    DEBITO = "Debito"
    CREDITO = "Credito"
    BOLETO = "Boleto"
    CHEQUE = "Cheque"
    

@dataclass
class Recebimento:
    """
    Representa um recebimento de dinheiro (entrada de caixa).

    Atributos:
        id: Identificador único no banco de dados (pode ser None antes de salvar).
        valor: Valor recebido.
        data: Data em que o recebimento foi registrado.
        forma_pagamento: Forma de pagamento utilizada (PIX, dinheiro, etc.).
        comprovante_caminho: Caminho opcional para um arquivo de comprovante.
    """
    id: Optional[int]
    valor: float
    data: date
    forma_pagamento: FormaPagamento
    comprovante_caminho: Optional[str] = None


@dataclass
class Despesa:
    """
    Representa uma despesa (saída de dinheiro).

    Atributos:
        id: Identificador único no banco de dados.
        valor: Valor da despesa.
        data: Data em que a despesa foi lançada.
        forma_pagamento: Forma de pagamento utilizada.
        descricao: Texto explicando do que se trata a despesa.
        eh_a_prazo: Indica se é uma conta a prazo (True) ou à vista (False).
        data_vencimento: Data de vencimento, usada quando eh_a_prazo=True.
        comprovante_caminho: Caminho opcional para um comprovante da despesa.
    """
    id: Optional[int]
    valor: float
    data: date
    forma_pagamento: FormaPagamento
    descricao: str
    eh_a_prazo: bool = False
    data_vencimento: Optional[date] = None
    comprovante_caminho: Optional[str] = None


@dataclass
class OrdemServico:
    """
    Representa uma ordem de serviço.

    Atributos:
        id: Identificador único no banco de dados.
        cliente: Nome ou identificação do cliente.
        descricao: Descrição do serviço a ser realizado.
        valor_total: Valor total da ordem de serviço.
        data: Data de emissão/registro da OS.
        foi_pago: Indica se a OS já foi totalmente paga.
        forma_pagamento: Forma de pagamento usada, quando já definido.
    """
    id: Optional[int]
    cliente: str
    descricao: str
    valor_total: float
    data: date
    foi_pago: bool
    forma_pagamento: Optional[FormaPagamento] = None


@dataclass
class Funcionario:
    """
    Representa um funcionário.

    Atributos:
        id: Identificador único.
        nome: Nome completo.
        cpf: Cadastro de Pessoa Física.
        telefone: Número de contato.
        cargo: Cargo ou função na empresa.
        foto_caminho: Caminho para o arquivo da foto.
        data_admissao: Data de contratação.
        dia_pagamento: Dia do mês para pagamento de salário.
        mes_decimo_terceiro: Mês planejado/realizado para o 13º salário (1-12).
        mes_ferias: Mês planejado/realizado para férias (1-12).
        data_demissao: Data de saída (None se estiver ativo).
    """
    id: Optional[int]
    nome: str
    cpf: str
    telefone: str
    cargo: str
    foto_caminho: Optional[str]
    data_admissao: date
    dia_pagamento: int
    mes_decimo_terceiro: Optional[int] = None
    mes_ferias: Optional[int] = None
    data_demissao: Optional[date] = None
