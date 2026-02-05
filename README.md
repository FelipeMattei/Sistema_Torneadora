# Sistema Financeiro - Torneadora

Um sistema simples e eficiente para gestão financeira e de pedidos de serviço.

## Funcionalidades
- **Receitas**: Registro de entradas com suporte a comprovantes.
- **Despesas**: Controle de contas pagas e a pagar (faturas).
- **Notas de Serviço**: Gestão de ordens de serviço e status de pagamento.
- **Funcionários**: Cadastro completo de funcionários.
- **Relatórios**: Geração de relatórios detalhados em Excel.
- **Backup**: Dados salvos localmente em SQLite (`financeiro.db`).

## Como rodar o projeto
Certifique-se de ter o Python instalado (3.8+).

1. Instale as dependências (se houver arquivo `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```
   *Dependências principais: PySide6, openpyxl*

2. Execute o sistema:
   ```bash
   python run.py
   ```

## Estrutura do Projeto
O código fonte está organizado dentro da pasta `app/`:

- `app/main.py`: Inicialização da aplicação.
- `app/database`: Conexão com o banco de dados.
- `app/models`: Definição das entidades (Receita, Despesa, etc.).
- `app/repositories`: Acesso a dados (CRUD).
- `app/services`: Regras de negócio.
- `app/ui`: Interface gráfica (Janelas, Diálogos, Estilos).
- `app/utils`: Funções utilitárias.
- `app/reports`: Gerador de Excel.

## Desenvolvimento
Para adicionar novas funcionalidades, siga o padrão de Arquitetura em Camadas:
1. Crie a entidade em `app/models`.
2. Adicione o método de persistência em `app/repositories`.
3. Adicione a regra de negócio em `app/services`.
4. Crie a interface em `app/ui`.
