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

# File: src/controllers/info_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    InfoController (Controller). O "cérebro" para o EditorPanel.
#    (Refatorado para gerir múltiplas associações via Checkboxes)

import logging
from PySide6.QtCore import QObject, Slot

from src.domain.app_state import AppState
from src.domain.entities import MapNode, MapEdge
from src.utils.i18n import I18nManager
from ui.editor.editor_panel import EditorPanel
from src.core.map_renderer import MapRenderer


class InfoController(QObject):
    """
    Controlador para o EditorPanel.
    
    Responsabilidade:
    - Ouvir os sinais do EditorPanel (View).
    - Atualizar o AppState (Model) quando 'Salvar' é clicado.
    - Gerir múltiplas associações de fontes locais (Checkboxes).
    - Orquestrar a exibição/ocultação do painel.
    - Comandar a limpeza do destaque (áurea) no MapRenderer.
    """
    
    def __init__(
        self,
        app_state: AppState,
        view: EditorPanel,
        map_renderer: MapRenderer,
        i18n: I18nManager
    ):
        super().__init__() 
        
        self._app_state = app_state
        self._view = view
        self._map_renderer = map_renderer
        self._i18n = i18n
        
        self._current_element = None

    def setup_connections(self):
        """Conecta os sinais da View aos slots deste controlador."""
        self._view.save_clicked.connect(self._on_save)
        self._view.close_clicked.connect(self.hide_panel)
        
        # --- 1. CONEXÃO REMOVIDA (Resolve o AttributeError) ---
        # (O sinal 'association_changed' do ComboBox foi removido da View)
        # self._view.association_changed.connect(self._on_association_changed)

    # --- Métodos Públicos (Chamados pelo MapController) ---

    @Slot(MapNode)
    def show_for_node(self, node: MapNode):
        """Exibe o painel com os dados de um Nó."""
        self._current_element = node
        self._prepare_view_data() # Prepara a lista de checkboxes
        
        t = self._i18n.t
        self._view.show_data(
            title=t("info_panel.title_node"),
            sumo_id=node.id,
            real_name=node.real_name
        )
        self._view.show()
        self._view.raise_()

    @Slot(MapEdge)
    def show_for_edge(self, edge: MapEdge):
        """Exibe o painel com os dados de uma Aresta."""
        self._current_element = edge
        self._prepare_view_data() # Prepara a lista de checkboxes
        
        t = self._i18n.t
        self._view.show_data(
            title=t("info_panel.title_edge"),
            sumo_id=edge.id,
            real_name=edge.real_name
        )
        self._view.show()
        self._view.raise_()

    @Slot()
    def hide_panel(self):
        """
        Esconde o painel, limpa o elemento atual E limpa a "áurea".
        """
        self._current_element = None
        self._view.hide()
        self._map_renderer.clear_highlight()

    # --- Métodos Privados Auxiliares ---

    # --- 2. MÉTODO ATUALIZADO (para Checkboxes) ---
    def _prepare_view_data(self):
        """
        Obtém as fontes disponíveis e as associações atuais do Modelo
        e atualiza a View (QListWidget de checkboxes).
        """
        if not self._current_element:
            return

        element_id = self._current_element.id

        # 1. Obter fontes locais disponíveis (livres ou já deste elemento)
        #
        available_sources = self._app_state.get_available_local_sources(element_id)

        # 2. Verificar quais fontes já estão associadas a este elemento
        #
        current_sources = self._app_state.get_sources_associated_with_element(element_id)
        # Cria um "set" (conjunto) de IDs para pesquisa rápida
        current_source_ids = {s.path for s in current_sources}
        
        # 3. Passa ambas as listas para a View
        #
        self._view.update_sources_list(available_sources, current_source_ids)

    # --- Slots Privados (Ouvem a View) ---

    # 3. SLOT REMOVIDO (Não há mais ComboBox)
    # @Slot(object)
    # def _on_association_changed(self, source_id: str | None):
    #     ...

    # --- 4. MÉTODO ATUALIZADO (para Checkboxes) ---
    @Slot(str)
    def _on_save(self, new_real_name: str):
        """
        Chamado quando o botão 'Salvar' na View é clicado.
        (Salva o Nome E a lista de associações dos Checkboxes)
        """
        if self._current_element:
            element_id = self._current_element.id
            
            # --- LÓGICA DE SALVAR ATUALIZADA ---
            
            # Ação 1: Salvar o Nome Real (como antes)
            logging.info(f"InfoController: Salvando '{new_real_name}' para o ID {element_id}")
            self._app_state.update_element_real_name(
                element_id, 
                new_real_name
            )
            
            # Ação 2: Salvar as Associações (lendo os checkboxes)
            
            # Lê os IDs de todas as caixas marcadas na View
            #
            selected_ids = self._view.get_selected_source_ids()
            
            logging.info(f"InfoController: Salvando associações {selected_ids} para o ID {element_id}")
            
            # Envia a lista completa de IDs para o Modelo
            #
            self._app_state.set_element_associations(
                element_id, 
                selected_ids
            )
            # --- FIM DA ALTERAÇÃO ---
            
            self.hide_panel()
        
        else:
            logging.warning("InfoController: 'Salvar' clicado, mas nenhum elemento estava selecionado.")