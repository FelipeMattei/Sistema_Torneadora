2. Um lugar para registrar recebimentos, com valor, comprovante(opcional), forma de pagamento, data;
3. Um lugar pra registrar despesas(contas, pagamentos em geral) com valor, comprovante, forma de pagamento, data, registrar contas a prazo(boleto, cheque, crédito);
4. Gerar ordem de serviço com a opção de colocar os meios de pagamento, se já foi pago, se ainda vai ser pago; A CONVERSAR;
5. Possibilidade de fazer o backup de todos os dados no sistema.


A ordem lógica pra ir montando o sistema é:

models.py → definir os “objetos do mundo real” (Recebimento, Despesa, OrdemServico, FormaPagamento). OK

repositories.py → criar as classes que fazem CRUD no banco usando Database. OK

services.py → juntar regras de negócio em uma classe tipo SistemaFinanceiro. 

interface.py → fazer a interface (menu de terminal ou GUI) chamando os serviços.

app.py → ponto de entrada que chama a interface.

