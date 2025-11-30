"""
Módulo de serviços/regras de negócio.

Centraliza a lógica de negócio do sistema, combinando modelos e
repositórios. Aqui ficam métodos mais "inteligentes", como registrar
um recebimento, lançar uma despesa a prazo ou gerar uma ordem de
serviço. A interface (UI) deve conversar com esta camada, e não
diretamente com o banco de dados.
"""


from datetime import date, timedelta
from typing import Optional, List

from database import Database
from models import Recebimento, Despesa, OrdemServico, FormaPagamento
from repositories import (
    RecebimentoRepositorio,
    DespesaRepositorio,
    OrdemServicoRepositorio,
)


class SistemaFinanceiro:
    """
    Classe principal de regras de negócio.

    Ela coordena operações de alto nível, como registrar um
    recebimento, lançar uma despesa a prazo, gerar uma ordem de
    serviço e calcular o saldo atual, delegando o acesso ao banco
    para os repositórios.
    """

    # ========= HELPERS INTERNOS =========

    def _filtrar_por_periodo(self, itens, get_data, periodo: str, ref: date):
        """
        periodo: 'todos', 'diario', 'semanal', 'mensal'
        ref: data de referência (hoje, por exemplo)
        """
        periodo = periodo.lower()
        if periodo == "todos":
            return list(itens)

        if periodo == "diario":
            return [x for x in itens if get_data(x) == ref]

        if periodo == "semanal":
            inicio = ref - timedelta(days=6)
            return [x for x in itens if inicio <= get_data(x) <= ref]

        if periodo == "mensal":
            return [x for x in itens if get_data(x).year == ref.year and get_data(x).month == ref.month]

        # padrão: sem filtro
        return list(itens)

    def __init__(self, db: Database):
       
        self.db = db

        # Repositórios especializados para cada tipo de entidade
        self.recebimentos_repo = RecebimentoRepositorio(self.db)
        self.despesas_repo = DespesaRepositorio(self.db)
        self.os_repo = OrdemServicoRepositorio(self.db)



     # ========= RECEBIMENTOS =========

    def registrar_recebimento(
        self,
        valor: float,
        forma_pagamento: FormaPagamento,
        data: Optional[date] = None,
        comprovante_caminho: Optional[str] = None,
    ) -> int:
        """
        Registra um recebimento no sistema.

        A data, se não for informada, assume a data de hoje. A interface
        (UI) é responsável por converter strings digitadas pelo usuário
        em tipos corretos (float, date, FormaPagamento) antes de chamar
        este método.
        """
        rec = Recebimento(
            id=None,
            valor=valor,
            data=data or date.today(),
            forma_pagamento=forma_pagamento,
            comprovante_caminho=comprovante_caminho,
        )
        return self.recebimentos_repo.criar(rec)

    def listar_recebimentos(self) -> List[Recebimento]:
        """
        Retorna todos os recebimentos cadastrados.
        """
        return self.recebimentos_repo.listar_todos()
    

    
    # ========= DESPESAS =========

    def registrar_despesa(
        self,
        valor: float,
        descricao: str,
        forma_pagamento: FormaPagamento,
        data: Optional[date] = None,
        comprovante_caminho: Optional[str] = None,
    ) -> int:
        """
        Registra uma despesa à vista (não a prazo).

        A data, se não for informada, assume a data de hoje.
        """
        desp = Despesa(
            id=None,
            valor=valor,
            data=data or date.today(),
            forma_pagamento=forma_pagamento,
            descricao=descricao,
            eh_a_prazo=False,
            data_vencimento=None,
            comprovante_caminho=comprovante_caminho,
        )
        return self.despesas_repo.criar(desp)

    def registrar_despesa_a_prazo(
        self,
        valor: float,
        descricao: str,
        forma_pagamento: FormaPagamento,
        data_vencimento: date,
        data_lancamento: Optional[date] = None,
        comprovante_caminho: Optional[str] = None,
    ) -> int:
        """
        Registra uma despesa a prazo (boleto, cheque, crédito, etc.).

        data_lancamento: quando a despesa foi registrada no sistema.
        data_vencimento: quando a conta efetivamente vence.
        """
        desp = Despesa(
            id=None,
            valor=valor,
            data=data_lancamento or date.today(),
            forma_pagamento=forma_pagamento,
            descricao=descricao,
            eh_a_prazo=True,
            data_vencimento=data_vencimento,
            comprovante_caminho=comprovante_caminho,
        )
        return self.despesas_repo.criar(desp)

    def listar_despesas(self) -> List[Despesa]:
        """
        Retorna todas as despesas cadastradas.
        """
        return self.despesas_repo.listar_todos()

    # ========= ORDENS DE SERVIÇO =========

    def gerar_ordem_servico(
        self,
        cliente: str,
        descricao: str,
        valor_total: float,
        foi_pago: bool = False,
        forma_pagamento: Optional[FormaPagamento] = None,
        data: Optional[date] = None,
    ) -> int:
        """
        Gera e salva uma nova ordem de serviço.
        """
        os_ = OrdemServico(
            id=None,
            cliente=cliente,
            descricao=descricao,
            valor_total=valor_total,
            data=data or date.today(),
            foi_pago= foi_pago,
            forma_pagamento=forma_pagamento,
        )
        return self.os_repo.criar(os_)

    def listar_ordens_servico(self) -> List[OrdemServico]:
        """
        Retorna todas as ordens de serviço cadastradas.
        """
        return self.os_repo.listar_todas()
    

        # ========= LISTAGENS FILTRADAS POR PERÍODO =========

    def listar_recebimentos_periodo(self, periodo: str, data_ref: date) -> List[Recebimento]:
        return self._filtrar_por_periodo(
            self.listar_recebimentos(),
            lambda r: r.data,
            periodo,
            data_ref,
        )

    def listar_despesas_periodo(self, periodo: str, data_ref: date) -> List[Despesa]:
        return self._filtrar_por_periodo(
            self.listar_despesas(),
            lambda d: d.data,
            periodo,
            data_ref,
        )

    def listar_ordens_servico_periodo(self, periodo: str, data_ref: date) -> List[OrdemServico]:
        return self._filtrar_por_periodo(
            self.listar_ordens_servico(),
            lambda o: o.data,
            periodo,
            data_ref,
        )

    # ========= FUNÇÕES DE APOIO / RESUMO =========

    def calcular_saldo(self) -> float:
        """
        Calcula o saldo simples do sistema:
        total de recebimentos - total de despesas.
        """
        total_recebimentos = sum(r.valor for r in self.listar_recebimentos())
        total_despesas = sum(d.valor for d in self.listar_despesas())
        return total_recebimentos - total_despesas
    
        # ========= ATUALIZAÇÕES =========

    def atualizar_recebimento(self, rec: Recebimento) -> None:
        self.recebimentos_repo.atualizar(rec)

    def atualizar_despesa(self, desp: Despesa) -> None:
        self.despesas_repo.atualizar(desp)

    def atualizar_ordem_servico(self, os_: OrdemServico) -> None:
        self.os_repo.atualizar(os_)

    def marcar_ordem_servico_como_paga(
        self,
        os_id: int,
        forma_pagamento: Optional[FormaPagamento] = None
    ) -> None:
        self.os_repo.marcar_como_pago(os_id, forma_pagamento)
