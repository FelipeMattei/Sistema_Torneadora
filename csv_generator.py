"""
Módulo Gerador de CSV.

Responsável por gerar relatórios em CSV a partir de dados tabulares.
Utiliza codificação UTF-8 com BOM e delimitador ponto-e-vírgula para
compatibilidade com Excel em locales portugueses.
"""

import csv
from typing import List, Tuple, Optional
from datetime import date


def gerar_csv_relatorio(
    caminho_saida: str,
    titulo: str,
    periodo_descricao: str,
    saldo_final: str,
    colunas: List[str],
    linhas: List[Tuple]
) -> bool:
    """
    Gera um arquivo CSV com cabeçalho informativo e dados tabulares.
    
    Args:
        caminho_saida: Caminho completo onde o CSV será salvo
        titulo: Título do relatório (ex: "Relatório de Receitas")
        periodo_descricao: Descrição do período filtrado
        saldo_final: Texto do saldo/total final formatado
        colunas: Lista com nomes das colunas
        linhas: Lista de tuplas, cada uma representando uma linha de dados
        
    Returns:
        True se o CSV foi gerado com sucesso, False caso contrário
    """
    try:
        # Abre arquivo com UTF-8 BOM para compatibilidade com Excel
        with open(caminho_saida, 'w', newline='', encoding='utf-8-sig') as arquivo:
            writer = csv.writer(arquivo, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            
            # Seção de cabeçalho
            writer.writerow([titulo])
            writer.writerow([f"Período: {periodo_descricao}"])
            writer.writerow([saldo_final])
            
            # Linha em branco
            writer.writerow([])
            
            # Cabeçalhos das colunas
            writer.writerow(colunas)
            
            # Dados
            for linha in linhas:
                linha_formatada = []
                for valor in linha:
                    if isinstance(valor, float):
                        # Formata números: mantém 2 casas decimais
                        valor_str = f"{valor:.2f}".replace('.', ',')
                    elif isinstance(valor, date):
                        # Formata datas como dd/MM/yyyy
                        valor_str = valor.strftime("%d/%m/%Y")
                    elif valor is None:
                        valor_str = ""
                    else:
                        valor_str = str(valor)
                    linha_formatada.append(valor_str)
                writer.writerow(linha_formatada)
        
        return True
        
    except Exception as e:
        print(f"Erro ao gerar CSV: {e}")
        return False
