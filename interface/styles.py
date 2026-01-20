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
QDialog#addEditEmployeeDialog,
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
    image: url(icons/down-arrow.png); /* Certifique-se que o ícone existe ou remova */
    width: 10px;
    height: 10px;
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
    image: url(icons/down-arrow.png);
    width: 10px;
    height: 10px;
}

/* 
   --- CALENDAR WIDGET ---
   Estilo crítico para corrigir calendário escuro/ilegível
*/
QCalendarWidget QWidget {
    background-color: #ffffff;
    color: #333333;
}

QCalendarWidget QToolButton {
    color: #333333;
    background: transparent;
    icon-size: 20px;
}

QCalendarWidget QMenu {
    background-color: #ffffff;
    color: #333333;
}

QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
}

/* Cabeçalho dos dias da semana (S, T, Q...) */
QCalendarWidget QTableView {
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
    gridline-color: #d0d0d0;
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

/*
    --- SCROLLBAR (Barra de Rolagem Moderna) ---
*/
QScrollBar:vertical {
    border: none;
    background: #f0f0f0;
    width: 6px;
    margin: 0px 0px 0px 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #c1c1c1;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #a8a8a8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/*
    --- SPINBOX (Seleção Numérica) ---
*/
QSpinBox {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #d0d0d0;
    padding: 8px 12px;
    color: #333;
}
QSpinBox:focus {
    border: 1px solid #00b33c;
}

/* Setas do SpinBox */
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 25px;
    border-left: 1px solid #d0d0d0;
    border-top-right-radius: 10px;
    background: transparent;
    margin-bottom: 1px;
}
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 25px;
    border-left: 1px solid #d0d0d0;
    border-bottom-right-radius: 10px;
    background: transparent;
    margin-top: 1px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #f0f0f0;
}
/* Icones simples para as setas (pode usar imagem se tiver, ou seta ascii/triangulo built-in)
   O Qt padrão desenha setas se não definirmos imagem, mas as vezes fica feio.
   Vamos tentar usar empty image e deixar o Qt desenhar a seta padrão clean ou definir cor.*/
QSpinBox::up-arrow {
    image: url(icons/up-arrow.png);
    width: 10px; height: 10px;
}
QSpinBox::down-arrow {
    image: url(icons/down-arrow.png);
    width: 10px; height: 10px;
}

/* 
   --- CORREÇÃO DE CORES (Inputs) ---
   Garantir fundo branco e texto escuro
*/
QLineEdit, QComboBox, QDateEdit, QSpinBox {
    color: #333333;
    background-color: #ffffff;
}

/* Popup do ComboBox (fundo branco explícito) */
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    selection-background-color: #00b33c;
    selection-color: #ffffff;
    color: #333333;
    outline: none;
}

/*
    --- MAIN WINDOW STYLES ---
    Estilos para a interface principal moderna
*/

/* Header */
QFrame#mainHeader {
    background-color: #2B4B7C;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E0E0E0;
}

/* Sidebar item hover */
QPushButton#sidebarItem {
    text-align: left;
    padding-left: 15px;
    font-size: 14px;
    font-weight: 500;
    color: #4A4A4A;
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
}

QPushButton#sidebarItem:hover {
    background-color: #F0F4F8;
    border-left: 3px solid #2B4B7C;
    color: #2B4B7C;
}

/* Financial Cards */
QFrame#financialCard {
    background-color: white;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
}

/* Action buttons */
QPushButton#actionButton {
    border-radius: 18px;
    font-size: 13px;
    font-weight: 600;
    padding: 0 20px;
    border: none;
}

QPushButton#actionButton:hover {
    opacity: 0.9;
}
"""
