"""
Módulo de acesso ao banco de dados.

Responsável por gerenciar a conexão com o banco (por exemplo, SQLite),
criar as tabelas necessárias na primeira execução e fornecer funções/
métodos genéricos para executar comandos SQL (inserir, consultar, etc.).
Ele não conhece regras de negócio, apenas lida com persistência de dados.
"""

import sqlite3

class Database:
    def __init__(self, caminho_banco: str = "financeiro.db"):
        self.caminho_banco = caminho_banco
        self._criar_tabelas()

    def _conectar(self):
        return sqlite3.connect(self.caminho_banco)
    
    def _criar_tabelas(self):
        conn = self._conectar()
        cur = conn.cursor()


        # Criar tabela dos recebimentos
        cur.execute("""
                    
            CREATE TABLE IF NOT EXISTS recebimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                forma_pagamento TEXT NOT NULL,
                comprovante_caminho TEXT)
        """)


        # Criar tabela das despesas
        cur.execute("""
            
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                forma_pagamento TEXT NOT NULL,
                descricao TEXT NOT NULL,
                eh_a_prazo INTEGER NOT NULL,
                data_vencimento TEXT,
                comprovante_caminho TEXT)
        """)


            # ORDENS DE SERVIÇO AGORA COM COLUNA data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ordens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor_total REAL NOT NULL,
                data TEXT NOT NULL,
                foi_pago INTEGER NOT NULL,
                forma_pagamento TEXT
            )
        """)
        
        # Criar tabela de funcionários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL,
                telefone TEXT,
                cargo TEXT,
                foto_caminho TEXT,
                data_admissao TEXT NOT NULL,
                dia_pagamento INTEGER NOT NULL,
                mes_decimo_terceiro INTEGER,
                mes_ferias INTEGER,
                data_demissao TEXT
            )
        """)


        conn.commit()
        conn.close()

    def executar(self, sql: str, params  = ()) -> int:
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(sql,params)
        conn.commit()
        last_id = cur.lastrowid
        conn.close()

        return last_id
    
    def consultar(self, sql: str, params = ()):
        conn = self._conectar()
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        return rows
    