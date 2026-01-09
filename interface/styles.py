"""
Módulo de Estilos (Styles).

Este arquivo contém as definições de CSS (QSS) usadas em toda a aplicação.
Separar os estilos em um arquivo próprio facilita a manutenção do design
visual e evita poluir o código lógico com strings de formatação.
"""

# Estilos gerais para diálogos e widgets
# Definimos cores, bordas, arredondamentos e comportamentos de foco aqui.
DIALOG_STYLES = """
/* 
   Configuração para diálogos translúcidos. 
   Os nomes (IDs) referenciam os objectNames definidos nas classes de diálogo.
*/
QDialog#novaReceitaDialog,
QDialog#novaDespesaDialog,
QDialog#novaNotaServicoDialog,
QDialog#relatorioGeralDialog {
    background: transparent;
}

/* Fonte base para todos os elementos dentro destes diálogos */
* {
    font-size: 15px;
}

/* Card principal que contém o conteúdo do diálogo (fundo cinza claro) */
QFrame#card {
    background-color: #E6E6E6;
    border-radius: 26px;
}

/* Títulos principais */
QLabel#title {
    font-size: 22px;
    font-weight: 800;
    color: #3D3D3D;
}

/* Subtítulos descritivos */
QLabel#subtitle {
    font-size: 17px;
    color: #555555;
}

/* Títulos de seção (ex: "Dados da receita", "Comprovante") */
QLabel#sectionTitle {
    font-size: 17px;
    font-weight: 700;
    color: #4A4A4A;
    margin-top: 12px;
    margin-bottom: 6px;
}

/* 
   --- CAMPOS DE ENTRADA (Inputs) ---
   Estilo unificado para Caixas de texto, Combos e Datas 
*/
QLineEdit, QComboBox, QDateEdit {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #d0d0d0;
    padding: 8px 12px;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
}

/* Efeito de foco: Borda verde suave ao clicar */
QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus {
    border: 1px solid #00b33c;
}

/* 
   --- COMBOBOX (Dropdown) ---
   Ajustes específicos para a seta e preenchimento 
*/
QComboBox {
    padding: 8px 40px 8px 14px;
    color: #555555;
}

/* Lista de opções do combobox (popup) */
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #d0d0d0;
    outline: 0;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
}

QComboBox QAbstractItemView::item {
    padding: 4px 16px;
}

/* Seta do combo (Drop-down arrow) */
QComboBox::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}

QComboBox::down-arrow {
    image: url(icons/right-arrow.png); /* Certifique-se que o ícone existe ou remova */
    width: 14px;
    height: 14px;
}

/* 
   --- DATE EDIT ---
   Ajuste similar ao combobox para o calendário 
*/
QDateEdit {
    padding-right: 32px;
}

QDateEdit::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}

QDateEdit::down-arrow {
    image: url(icons/right-arrow.png);
    width: 14px;
    height: 14px;
}

/* 
   --- BOTÕES (Buttons) ---
*/

/* Botão de fechar (X) no topo */
QPushButton#closeButton {
    border: none;
    background: transparent;
    font-size: 16px;
}
QPushButton#closeButton:hover {
    background-color: rgba(0,0,0,0.06);
    border-radius: 10px;
}

/* Botão de selecionar arquivo (setinha para baixo) */
QPushButton#fileButton {
    background-color: #ffffff;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    border: 1px solid #d0d0d0;
}
/* Ajuste para colar visualmente no input de texto ao lado */
QPushButton#fileButton {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
}
QFrame#comprovanteFrame QLineEdit {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    border-right: none;
}

/* Botão Primário (Verde - Ação Principal de Salvar/Confirmar) */
QPushButton#primaryButton {
    background-color: #00b33c;
    color: white;
    border-radius: 10px;
    padding: 10px 25px;
    border: 1px solid #9F9F9F;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background-color: #00a534;
}

/* Botão Secundário (Cinza - Cancelar/Fechar) */
QPushButton#secondaryButton {
    background-color: #d9d9d9;
    color: #555555;
    border-radius: 10px;
    padding: 10px 38px;
    border: 1px;
    font-weight: 600;
}
QPushButton#secondaryButton:hover {
    background-color: #cfcfcf;
}

/* 
   --- CHECKBOXES ---
*/
QCheckBox#prazoCheck, QCheckBox#PagoCheck {
    font-size: 17px;
    font-weight: 700;
    color: #4A4A4A;
}

QCheckBox#prazoCheck::indicator, QCheckBox#PagoCheck::indicator {
    margin-top: 0px;
}
"""
