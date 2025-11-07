# SFusion (SYNAPSE Fusion) Mapper
#
# Copyright (C) 2025 Gabriel Moraes - Noxfort Labs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# File: ui/sources/sources_panel.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    SourcesPanel (View). O painel lateral direito (QDockWidget)
#    que lista as fontes de dados carregadas.

import logging
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QRadioButton,
    QHBoxLayout,
    QFrame
)

# 1. Importar I18nManager
from src.utils.i18n import I18nManager
from src.domain.entities import DataSource


class SourcesPanel(QWidget):
    """
    View do painel lateral.
    Exibe a lista de DataSources e os controlos de associação.
    """
    
    # Sinais para o SourcesController
    source_selection_changed = Signal(str) # Emite o ID (caminho) da fonte
    association_type_changed = Signal(str) # Emite "global" ou "local"

    # --- 2. Alteração Principal: Corrigir o __init__ ---
    def __init__(self, i18n: I18nManager, parent: QWidget | None = None):
        """
        Inicializa o painel de fontes.
        
        :param i18n: O gestor de internacionalização (tradução).
        :param parent: O widget "Pai" (normalmente a MainWindow).
        """
        # 3. Chamar o super() com o 'parent' correto
        super().__init__(parent)
        
        # 4. Armazenar o i18n corretamente
        self._i18n = i18n
        self._init_ui()
        logging.info("SourcesPanel (View) inicializado.")

    def _init_ui(self):
        """Constrói os componentes da UI."""
        t = self._i18n.t
        
        # Layout principal do painel
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # --- 1. Caixa de Lista de Fontes ---
        sources_group = QGroupBox(t("sources_panel.title"))
        sources_layout = QVBoxLayout(sources_group)
        
        self.sources_list_widget = QListWidget()
        self.sources_list_widget.setSpacing(3)
        
        # Conecta o sinal da UI
        self.sources_list_widget.currentItemChanged.connect(
            self._on_list_selection_changed
        )
        
        sources_layout.addWidget(self.sources_list_widget)
        layout.addWidget(sources_group)

        # --- 2. Caixa de Controlo de Associação ---
        association_group = QGroupBox(t("sources_panel.association_title"))
        association_layout = QVBoxLayout(association_group)
        association_layout.setSpacing(10)

        self.radio_global = QRadioButton(t("sources_panel.radio_global"))
        self.radio_global.setToolTip(t("sources_panel.radio_global_tip"))
        
        self.radio_local = QRadioButton(t("sources_panel.radio_local"))
        self.radio_local.setToolTip(t("sources_panel.radio_local_tip"))
        self.radio_local.setChecked(True) # Padrão
        
        # Conecta os sinais da UI
        self.radio_global.toggled.connect(self._on_radio_toggled)
        
        association_layout.addWidget(self.radio_global)
        association_layout.addWidget(self.radio_local)
        
        # (Desativado até que uma fonte seja selecionada)
        association_group.setEnabled(False)
        self.association_group = association_group # Salva referência

        layout.addWidget(association_group)

        # Espaçador para empurrar tudo para cima
        layout.addStretch(1)

    # --- Slots Internos (Emitem Sinais para o Controller) ---

    @Slot(QListWidgetItem, QListWidgetItem)
    def _on_list_selection_changed(self, current: QListWidgetItem, previous):
        """Chamado pela QListWidget quando a seleção muda."""
        if current:
            # Ativa o painel de associação
            self.association_group.setEnabled(True)
            
            # Obtém o ID (path) armazenado no item
            source_id = current.data(Qt.UserRole)
            self.source_selection_changed.emit(source_id)
        else:
            # Desativa o painel se nada estiver selecionado
            self.association_group.setEnabled(False)
            self.source_selection_changed.emit("")

    @Slot(bool)
    def _on_radio_toggled(self, checked: bool):
        """Chamado quando o Radio 'Global' muda (implica o 'Local')."""
        if checked:
            self.association_type_changed.emit("global")
        else:
            self.association_type_changed.emit("local")

    # --- Métodos Públicos (Chamados pelo Controller) ---

    @Slot(list)
    def update_sources_list(self, data_sources: list[DataSource]):
        """Atualiza a QListWidget com os dados do AppState."""
        self.sources_list_widget.clear()
        
        if not data_sources:
            # (Opcional: Mostrar um item "Nenhuma fonte...")
            return
            
        for source in data_sources:
            # Usa o nome da pasta como o texto
            item = QListWidgetItem(source.name)
            item.setToolTip(f"Caminho: {source.path}")
            
            # Armazena o ID (caminho) no item
            item.setData(Qt.UserRole, source.path) 
            
            self.sources_list_widget.addItem(item)
    
    @Slot(str)
    def set_selected_source(self, source_id: str):
        """Define a seleção na lista (ex: ao carregar um .db)."""
        if not source_id:
            self.sources_list_widget.clearSelection()
            return
            
        for i in range(self.sources_list_widget.count()):
            item = self.sources_list_widget.item(i)
            if item.data(Qt.UserRole) == source_id:
                item.setSelected(True)
                return

    @Slot(str)
    def set_association_type(self, assoc_type: str):
        """Define os botões de rádio (ex: ao selecionar um item)."""
        # Desconecta temporariamente os sinais para evitar loop
        self.radio_global.toggled.disconnect(self._on_radio_toggled)
        
        if assoc_type == "global":
            self.radio_global.setChecked(True)
        else:
            self.radio_local.setChecked(True)
            
        # Reconecta os sinais
        self.radio_global.toggled.connect(self._on_radio_toggled)