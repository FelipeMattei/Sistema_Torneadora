import sys
import os
from datetime import date

# Add current directory to path
sys.path.append(os.getcwd())

from database import Database
from services import SistemaFinanceiro
from models import Funcionario

def verify():
    print("Testing Employee Module Backend...")
    
    # Use in-memory DB or temporary file for testing
    db_path = "test_verify.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = Database(db_path)
    sistema = SistemaFinanceiro(db)
    
    # 1. Test Creation
    print("1. Testing Creation...")
    sistema.registrar_funcionario(
        nome="João Silva",
        cpf="123.456.789-00",
        telefone="(11) 99999-9999",
        cargo="Torneiro",
        data_admissao=date(2023, 1, 15),
        dia_pagamento=5,
        mes_decimo_terceiro=12,
        mes_ferias=None
    )
    
    funcs = sistema.listar_funcionarios()
    assert len(funcs) == 1
    f1 = funcs[0]
    assert f1.nome == "João Silva"
    assert f1.mes_decimo_terceiro == 12
    print("   Creation OK")
    
    # 2. Test Update
    print("2. Testing Update...")
    f1.cargo = "Mestre de Obras"
    f1.mes_ferias = 7
    sistema.atualizar_funcionario(f1)
    
    funcs = sistema.listar_funcionarios()
    assert len(funcs) == 1
    f1_updated = funcs[0]
    assert f1_updated.cargo == "Mestre de Obras"
    assert f1_updated.mes_ferias == 7
    print("   Update OK")
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Backend Verification Successful!")

if __name__ == "__main__":
    verify()
