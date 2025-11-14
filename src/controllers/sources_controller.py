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

# File: src/controllers/sources_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    SourcesController (Controller). O "cérebro" para o SourcesPanel.
#    (Modificado para lidar com o menu de clique-direito)

import logging
from PySide6.QtCore import QObject, Slot, Qt

from src.domain.app_state import AppState
from ui.sources.sources_panel import SourcesPanel
from src.utils.i18n import I18nManager
from src.domain.entities import DataSource


class SourcesController(QObject):
    """
    Controlador para o SourcesPanel.
    
    Responsabilidade:
    - Ouvir o AppState (Model) e atualizar a lista da View.
    - Ouvir a View (seleção de lista e menu) e atualizar o AppState (Model).
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
        
        # --- 1. ALTERAÇÃO DE LÓGICA (Novas conexões) ---
        
        # Conexões Antigas (clique esquerdo)
        self._view.source_selection_changed.connect(
            self._on_source_selected
        )
        
        # Novas Conexões (clique-direito vindos do)
        self._view.source_delete_requested.connect(
            self._on_source_delete
        )
        self._view.source_modify_type_requested.connect(
            self._on_source_modify_type
        )
        # --- FIM DA ALTERAÇÃO ---
        
        # Conexões do Modelo para a View
        self._app_state.data_sources_changed.connect(
            self._on_model_sources_updated
        )
        self._app_state.data_association_changed.connect(
            self._on_model_association_updated
        )

    # --- Slots Privados (Ouvem a View) ---

    @Slot(str)
    def _on_source_selected(self, source_id: str):
        """Chamado pela View (clique-esquerdo). Atualiza o Modelo."""
        self._app_state.set_selected_data_source(source_id)
        
        source = self._app_state.get_data_source_by_id(source_id)
        if source:
            # Atualiza o visor de rádio (informativo)
            # .value obtém a string ("GLOBAL" ou "LOCAL") do Enum
            self._view.set_association_type(source.association_type.value)
        else:
            self._view.set_association_type("LOCAL") # Padrão

    # --- 2. NOVOS SLOTS (Ouvem o menu de clique-direito) ---

    @Slot(str)
    def _on_source_delete(self, source_id: str):
        """Chamado pela View (clique-direito->Deletar). Atualiza o Modelo."""
        logging.info(f"SourcesController: Pedido para deletar fonte: {source_id}")
        
        # Chama o método do Modelo
        self._app_state.delete_data_source(source_id)

    @Slot(str)
    def _on_source_modify_type(self, source_id: str):
        """Chamado pela View (clique-direito->Modificar). Atualiza o Modelo."""
        logging.info(f"SourcesController: Pedido para modificar tipo da fonte: {source_id}")
        
        # Chama o método do Modelo
        self._app_state.toggle_source_association_type(source_id)
    
    # --- FIM DOS NOVOS SLOTS ---

    # --- Slots Privados (Ouvem o Modelo) ---
    
    @Slot(list)
    def _on_model_sources_updated(self, sources_list: list[DataSource]):
        """Chamado pelo AppState. Atualiza a lista na View."""
        self._view.update_sources_list(sources_list)

    @Slot(str, str)
    def _on_model_association_updated(self, source_id: str, assoc_type_or_id: str):
        """Chamado pelo AppState. Atualiza os rádios na View."""
        
        current_view_selection = self._view.sources_list_widget.currentItem()
        if current_view_selection:
            current_selected_id = current_view_selection.data(Qt.UserRole)
            if current_selected_id == source_id:
                
                if assoc_type_or_id.upper() in ["GLOBAL", "LOCAL"]:
                    self._view.set_association_type(assoc_type_or_id)