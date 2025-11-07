# SFusion (SYNAPSE Fusion) Mapper
#
# Copyright (C) 2025 Gabriel Moraes - Noxfort Labs
#
# Este programa é software livre: pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral Affero GNU como publicada pela
# Free Software Foundation, quer a versão 3 da Licença, ou
# (à sua opção) qualquer versão posterior.
#
# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Veja a
# Licença Pública Geral Affero GNU para mais detalhes.
#
# Deveria ter recebido uma cópia da Licença Pública Geral Affero GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

# File: ui/editor/editor_panel.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    EditorPanel (View). O painel lateral esquerdo
#    para editar metadados de Nós/Arestas.
#    (Refatoração do InfoPanel flutuante)

import logging
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy
)

# --- CORREÇÃO PRINCIPAL AQUI ---
# Esta linha estava a importar 'EditorPanel' (errado).
# Deve importar o 'I18nManager'.
from src.utils.i18n import I18nManager
# --- FIM DA CORREÇÃO ---


class EditorPanel(QWidget):
    """
    View do painel lateral esquerdo (Editor).
    Permite ao utilizador ver o ID do SUMO e editar o "Nome Real".
    """
    
    # Sinais para o InfoController (exatamente os mesmos do InfoPanel)
    save_clicked = Signal(str)
    close_clicked = Signal()

    def __init__(self, i18n: I18nManager, parent: QWidget | None = None):
        """
        Inicializa o painel editor.
        
        :param i18n: O gestor de internacionalização (tradução).
        :param parent: O widget "Pai" (normalmente a MainWindow).
        """
        super().__init__(parent)
        
        self._i18n = i18n
        self._current_element_id = None
        self._current_element_type = None
        
        self._init_ui()
        self.hide() # Começa escondido
        logging.info("EditorPanel (View) inicializado.")

    def _init_ui(self):
        """Constrói os componentes da UI."""
        t = self._i18n.t
        
        # Layout principal (vertical) para este QWidget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Usamos um QGroupBox para manter o título e a borda
        group_box = QGroupBox(t("info_panel.title"))
        main_layout.addWidget(group_box)
        
        # Layout (vertical) dentro do GroupBox
        content_layout = QVBoxLayout(group_box)

        # 1. Layout de Formulário (para os campos)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Campo 1: ID do SUMO (Apenas leitura)
        self.sumo_id_label = QLabel(t("info_panel.sumo_id"))
        self.sumo_id_value = QLineEdit()
        self.sumo_id_value.setReadOnly(True)
        self.sumo_id_value.setStyleSheet("background-color: #EEEEEE;")
        form_layout.addRow(self.sumo_id_label, self.sumo_id_value)

        # Campo 2: Nome Real (Editável)
        self.real_name_label = QLabel(t("info_panel.real_name"))
        self.real_name_input = QLineEdit()
        self.real_name_input.setPlaceholderText(t("info_panel.real_name_placeholder"))
        form_layout.addRow(self.real_name_label, self.real_name_input)
        
        content_layout.addLayout(form_layout)

        # 2. Layout de Botões (Salvar, Fechar)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Espaçador para empurrar os botões para a direita
        button_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        # Botão Fechar (agora esconde o painel)
        self.close_button = QPushButton(t("info_panel.button_close"))
        self.close_button.clicked.connect(self.close_clicked)
        button_layout.addWidget(self.close_button)

        # Botão Salvar
        self.save_button = QPushButton(t("info_panel.button_save"))
        self.save_button.setDefault(True) # Ativado com "Enter"
        self.save_button.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        content_layout.addLayout(button_layout)
        
        # Define a largura mínima do painel
        self.setMinimumWidth(250)


    def _on_save_clicked(self):
        """Slot interno para emitir o sinal de 'save_clicked'."""
        new_name = self.real_name_input.text()
        self.save_clicked.emit(new_name)

    # --- Métodos Públicos (Chamados pelo Controller) ---

    @Slot(str, str, str)
    def show_data(self, title: str, sumo_id: str, real_name: str | None):
        """Atualiza os campos com os dados do elemento."""
        
        # O group_box não é 'self' aqui, precisamos de uma referência
        # Vamos encontrar o QGroupBox que criámos
        group_box = self.findChild(QGroupBox)
        if group_box:
            group_box.setTitle(title) # ex: "Editar Nó" ou "Editar Rua"
        
        self.sumo_id_value.setText(sumo_id)
        
        if real_name:
            self.real_name_input.setText(real_name)
        else:
            self.real_name_input.clear()
            
        # Foca o campo de input
        self.real_name_input.setFocus()
        self.real_name_input.selectAll()