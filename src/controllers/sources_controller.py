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

# File: src/controllers/sources_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    SourcesController (Controller). O "cérebro" para o SourcesPanel.

import logging
# --- 1. CORREÇÃO AQUI ---
# Adicionamos 'Qt' à importação
from PySide6.QtCore import QObject, Slot, Qt

# Importar os tipos corretos
from src.domain.app_state import AppState
from ui.sources.sources_panel import SourcesPanel
from src.utils.i18n import I18nManager
from src.domain.entities import DataSource # Necessário para o slot


class SourcesController(QObject):
    """
    Controlador para o SourcesPanel.
    
    Responsabilidade:
    - Ouvir o AppState (Model) e atualizar a lista da View.
    - Ouvir a View (sinais) e atualizar o AppState (Model).
    """
    
    def __init__(
        self,
        app_state: AppState,
        view: SourcesPanel,
        i18n: I18nManager
    ):
        """
        Inicializa o controlador.
        
        :param app_state: A "Fonte Única da Verdade".
        :param view: A View (SourcesPanel) que este controlador gere.
        :param i18n: O gestor de internacionalização.
        """
        super().__init__() 
        
        self._app_state = app_state
        self._view = view
        self._i18n = i18n
        
        logging.info("SourcesController (Controlador) inicializado.")

    def setup_connections(self):
        """Conecta os sinais do Modelo e da View."""
        
        # 1. Quando a View muda, atualiza o Modelo
        self._view.source_selection_changed.connect(
            self._on_source_selected
        )
        self._view.association_type_changed.connect(
            self._on_association_changed
        )
        
        # 2. Quando o Modelo muda, atualiza a View
        # (Estes sinais vêm do AppState)
        self._app_state.data_sources_changed.connect(
            self._on_model_sources_updated
        )
        self._app_state.data_association_changed.connect(
            self._on_model_association_updated
        )

    # --- Slots Privados (Ouvem a View) ---

    @Slot(str)
    def _on_source_selected(self, source_id: str):
        """Chamado pela View. Atualiza o estado de seleção no Modelo."""
        self._app_state.set_selected_data_source(source_id)
        
        # Também atualiza os botões de rádio da View
        source = self._app_state.get_data_source_by_id(source_id)
        if source:
            self._view.set_association_type(source.association_type)

    @Slot(str)
    def _on_association_changed(self, assoc_type: str):
        """Chamado pela View (rádios). Atualiza a associação no Modelo."""
        self._app_state.update_selected_source_association(assoc_type)

    # --- Slots Privados (Ouvem o Modelo) ---
    
    @Slot(list)
    def _on_model_sources_updated(self, sources_list: list[DataSource]):
        """Chamado pelo AppState. Atualiza a lista na View."""
        self._view.update_sources_list(sources_list)

    @Slot(str, str)
    def _on_model_association_updated(self, source_id: str, assoc_type: str):
        """Chamado pelo AppState. Atualiza os rádios na View."""
        
        # Verifica se o item alterado é o que está selecionado
        current_view_selection = self._view.sources_list_widget.currentItem()
        if current_view_selection:
            # Esta linha agora funciona porque 'Qt' foi importado
            current_selected_id = current_view_selection.data(Qt.UserRole)
            if current_selected_id == source_id:
                self._view.set_association_type(assoc_type)