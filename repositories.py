"""
Módulo de repositórios (camada de persistência).

Responsável por transformar objetos de modelo (por exemplo, Recebimento,
Despesa, OrdemServico) em registros no banco de dados e vice-versa.
Cada repositório cuida do CRUD de uma entidade específica, utilizando
a classe Database para executar os comandos SQL.
"""

from datetime import date
from typing import List

from database import Database
from models import Recebimento, Despesa, OrdemServico, FormaPagamento, Funcionario




class RecebimentoRepositorio:
    def __init__(self, db: Database):
        self.db = db
    
    def criar(self, rec: Recebimento) -> int:
        sql = """
            INSERT INTO recebimentos (valor, data, forma_pagamento, comprovante_caminho)
            VALUES (?, ?, ?, ?)
            """
        params = (
            rec.valor,
            rec.data.isoformat(),         # date -> "YYYY-MM-DD"
            rec.forma_pagamento.value,    # FormaPagamento.PIX -> "pix"
            rec.comprovante_caminho
        )

        return self.db.executar(sql, params)


    def atualizar(self, rec: Recebimento) -> None:
        if rec.id is None:
            raise ValueError("Recebimento precisa ter id para atualizar.")
        sql = """
            UPDATE recebimentos
            SET valor = ?,
                data = ?,
                forma_pagamento = ?,
                comprovante_caminho = ?
            WHERE id = ?
        """
        params = (
            rec.valor,
            rec.data.isoformat(),
            rec.forma_pagamento.value,
            rec.comprovante_caminho,
            rec.id,
        )
        self.db.executar(sql, params)


    def listar_todos(self) -> List[Recebimento]:
        sql = "SELECT id, valor, data, forma_pagamento, comprovante_caminho FROM recebimentos"
        rows = self.db.consultar(sql)

        recebimentos: List[Recebimento] = []
        for r in rows:
            recebimentos.append(
                Recebimento(
                    id=r[0],
                    valor=r[1],
                    data=date.fromisoformat(r[2]),      # "YYYY-MM-DD" -> date
                    forma_pagamento=FormaPagamento(r[3]),
                    comprovante_caminho=r[4]
                )
            )
        return recebimentos
    

class DespesaRepositorio:
    def __init__(self, db: Database):
        self.db = db

    def criar(self, despesa: Despesa) -> int:

        sql ="""
        INSERT INTO despesas (
            valor,
            data,
            forma_pagamento,
            descricao,
            eh_a_prazo,
            data_vencimento,
            comprovante_caminho
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            despesa.valor,
            despesa.data.isoformat(),             # date -> "YYYY-MM-DD"
            despesa.forma_pagamento.value,        # FormaPagamento -> str
            despesa.descricao,
            1 if despesa.eh_a_prazo else 0,
            despesa.data_vencimento.isoformat() if despesa.data_vencimento else None,
            despesa.comprovante_caminho
        )

        return self.db.executar(sql, params)
    

    def atualizar(self, despesa: Despesa) -> None:
        if despesa.id is None:
            raise ValueError("Despesa precisa ter id para atualizar.")
        sql = """
            UPDATE despesas
            SET valor = ?,
                data = ?,
                forma_pagamento = ?,
                descricao = ?,
                eh_a_prazo = ?,
                data_vencimento = ?,
                comprovante_caminho = ?
            WHERE id = ?
        """
        params = (
            despesa.valor,
            despesa.data.isoformat(),
            despesa.forma_pagamento.value,
            despesa.descricao,
            1 if despesa.eh_a_prazo else 0,
            despesa.data_vencimento.isoformat() if despesa.data_vencimento else None,
            despesa.comprovante_caminho,
            despesa.id,
        )
        self.db.executar(sql, params)


    def listar_todos(self) -> List[Despesa]:
        sql = """
        SELECT id,
               valor,
               data,
               forma_pagamento,
               descricao,
               eh_a_prazo,
               data_vencimento,
               comprovante_caminho
        FROM despesas
        """
        rows = self.db.consultar(sql)

        despesas: List[Despesa] = []
        for r in rows:
            despesas.append(
                Despesa(
                    id=r[0],
                    valor=r[1],
                    data=date.fromisoformat(r[2]),
                    forma_pagamento=FormaPagamento(r[3]),
                    descricao=r[4],
                    eh_a_prazo=bool(r[5]),
                    data_vencimento=date.fromisoformat(r[6]) if r[6] else None,
                    comprovante_caminho=r[7]
                )
            )
        return despesas


class OrdemServicoRepositorio:
    def __init__(self, db: Database):
        self.db = db

    def criar(self, os_: OrdemServico) -> int:
        sql = """
        INSERT INTO ordens_servico (
            cliente,
            descricao,
            valor_total,
            data,
            foi_pago,
            forma_pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            os_.cliente,
            os_.descricao,
            os_.valor_total,
            os_.data.isoformat(),
            1 if os_.foi_pago else 0,
            os_.forma_pagamento.value if os_.forma_pagamento else None
        )
        return self.db.executar(sql, params)


    def listar_todas(self) -> List[OrdemServico]:
        sql = """
        SELECT id,
            cliente,
            descricao,
            valor_total,
            data,
            foi_pago,
            forma_pagamento
        FROM ordens_servico
        """
        rows = self.db.consultar(sql)

        ordens: List[OrdemServico] = []
        for r in rows:
            ordens.append(
                OrdemServico(
                    id=r[0],
                    cliente=r[1],
                    descricao=r[2],
                    valor_total=r[3],
                    data=date.fromisoformat(r[4]),
                    foi_pago=bool(r[5]),
                    forma_pagamento=FormaPagamento(r[6]) if r[6] else None
                )
            )

        return ordens
    
    def atualizar(self, os_: OrdemServico) -> None:
        if os_.id is None:
            raise ValueError("Ordem de serviço precisa ter id para atualizar.")
        sql = """
            UPDATE ordens_servico
            SET cliente = ?,
                descricao = ?,
                valor_total = ?,
                data = ?,
                foi_pago = ?,
                forma_pagamento = ?
            WHERE id = ?
        """
        params = (
            os_.cliente,
            os_.descricao,
            os_.valor_total,
            os_.data.isoformat(),
            1 if os_.foi_pago else 0,
            os_.forma_pagamento.value if os_.forma_pagamento else None,
            os_.id,
        )
        self.db.executar(sql, params)


    def marcar_como_pago(self, os_id: int, forma_pagamento: FormaPagamento) -> None:
        sql = """
            UPDATE ordens_servico
            SET foi_pago = 1,
                forma_pagamento = ?
            WHERE id = ?
        """
        fp_val = forma_pagamento.value if forma_pagamento else None
        self.db.executar(sql, (fp_val, os_id))


class FuncionarioRepositorio:
    def __init__(self, db: Database):
        self.db = db

    def criar(self, func: Funcionario) -> int:
        sql = """
            INSERT INTO funcionarios (
                nome,
                cpf,
                telefone,
                cargo,
                foto_caminho,
                data_admissao,
                dia_pagamento,
                mes_decimo_terceiro,
                mes_ferias,
                data_demissao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            func.nome,
            func.cpf,
            func.telefone,
            func.cargo,
            func.foto_caminho,
            func.data_admissao.isoformat(),
            func.dia_pagamento,
            func.mes_decimo_terceiro,
            func.mes_ferias,
            func.data_demissao.isoformat() if func.data_demissao else None
        )
        return self.db.executar(sql, params)

    def atualizar(self, func: Funcionario) -> None:
        if func.id is None:
            raise ValueError("Funcionário precisa ter id para atualizar.")
        sql = """
            UPDATE funcionarios
            SET nome = ?,
                cpf = ?,
                telefone = ?,
                cargo = ?,
                foto_caminho = ?,
                data_admissao = ?,
                dia_pagamento = ?,
                mes_decimo_terceiro = ?,
                mes_ferias = ?,
                data_demissao = ?
            WHERE id = ?
        """
        params = (
            func.nome,
            func.cpf,
            func.telefone,
            func.cargo,
            func.foto_caminho,
            func.data_admissao.isoformat(),
            func.dia_pagamento,
            func.mes_decimo_terceiro,
            func.mes_ferias,
            func.data_demissao.isoformat() if func.data_demissao else None,
            func.id,
        )
        self.db.executar(sql, params)

    def listar_todos(self) -> List[Funcionario]:
        sql = """
            SELECT id,
                   nome,
                   cpf,
                   telefone,
                   cargo,
                   foto_caminho,
                   data_admissao,
                   dia_pagamento,
                   mes_decimo_terceiro,
                   mes_ferias,
                   data_demissao
            FROM funcionarios
        """
        rows = self.db.consultar(sql)
        funcionarios = []
        for r in rows:
            funcionarios.append(
                Funcionario(
                    id=r[0],
                    nome=r[1],
                    cpf=r[2],
                    telefone=r[3],
                    cargo=r[4],
                    foto_caminho=r[5],
                    data_admissao=date.fromisoformat(r[6]),
                    dia_pagamento=r[7],
                    mes_decimo_terceiro=r[8],
                    mes_ferias=r[9],
                    data_demissao=date.fromisoformat(r[10]) if r[10] else None
                )
            )
        return funcionarios





        