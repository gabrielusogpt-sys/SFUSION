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

# File: src/domain/app_state.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    AppState (Model). A "Fonte Única da Verdade" (Single Source of Truth)
#    para o estado da aplicação.

import logging
from PySide6.QtCore import QObject, Signal # <-- 1. Importar QObject e Signal
from .entities import MapNode, MapEdge, DataSource


# 2. Fazer AppState herdar de QObject
class AppState(QObject):
    """
    Armazena o estado atual da aplicação na memória.
    Atua como a "Fonte Única da Verdade".
    Emite sinais quando os dados são alterados.
    """
    
    # --- 3. Definir os sinais que os Controladores irão ouvir ---
    
    # Sinal emitido quando novos dados de mapa (nós/arestas) são carregados
    map_data_loaded = Signal()
    
    # Sinal emitido quando a lista de fontes de dados muda (adicionada/removida)
    # Emite a lista [list(DataSource)]
    data_sources_changed = Signal(list) 
    
    # Sinal emitido quando a associação de uma fonte muda
    # Emite (source_id: str, association_type: str)
    data_association_changed = Signal(str, str)


    # 4. Adicionar o __init__ e chamar super()
    def __init__(self):
        super().__init__()
        
        # Dados do Mapa
        self._nodes: list[MapNode] = []
        self._edges: list[MapEdge] = []
        
        # Caches para acesso rápido (ex: cliques)
        self._nodes_by_id: dict[str, MapNode] = {}
        self._edges_by_id: dict[str, MapEdge] = {}

        # Dados das Fontes
        self._data_sources: list[DataSource] = []
        self._sources_by_path: dict[str, DataSource] = {}
        
        # Estado da UI
        self._selected_source_path: str | None = None

    # --- Métodos de Mapa ---

    def set_map_data(self, nodes: list[MapNode], edges: list[MapEdge]):
        """Define (ou limpa) os dados do mapa."""
        self._nodes = nodes
        self._edges = edges
        
        # Recria os caches
        self._nodes_by_id = {node.id: node for node in nodes}
        self._edges_by_id = {edge.id: edge for edge in edges}
        
        logging.info(f"AppState: Dados do mapa atualizados. {len(nodes)} nós, {len(edges)} arestas.")
        
        # 5. Emitir o sinal que o MapController estava à espera
        self.map_data_loaded.emit()

    def get_all_nodes(self) -> list[MapNode]:
        return self._nodes

    def get_all_edges(self) -> list[MapEdge]:
        return self._edges

    def get_node_by_id(self, node_id: str) -> MapNode | None:
        return self._nodes_by_id.get(node_id)

    def get_edge_by_id(self, edge_id: str) -> MapEdge | None:
        return self._edges_by_id.get(edge_id)

    def update_element_real_name(self, element_id: str, real_name: str):
        """Atualiza o 'real_name' de um nó ou aresta."""
        element = self.get_node_by_id(element_id) or self.get_edge_by_id(element_id)
        
        if element:
            # Garante que None é salvo se o texto estiver vazio
            element.real_name = real_name if real_name else None
            logging.info(f"AppState: 'real_name' atualizado para '{element_id}'")
        else:
            logging.warning(f"AppState: Tentativa de atualizar nome de elemento desconhecido: '{element_id}'")

    # --- Métodos de Fonte de Dados ---

    def add_data_source(self, source: DataSource):
        """Adiciona uma nova fonte de dados."""
        if source.path in self._sources_by_path:
            logging.warning(f"AppState: Fonte de dados '{source.path}' já existe.")
            return
            
        self._data_sources.append(source)
        self._sources_by_path[source.path] = source
        
        # Emite o sinal com a *nova lista completa*
        self.data_sources_changed.emit(self._data_sources)

    def get_all_data_sources(self) -> list[DataSource]:
        return self._data_sources

    def get_data_source_by_id(self, source_id: str) -> DataSource | None:
        return self._sources_by_path.get(source_id)

    def set_selected_data_source(self, source_id: str | None):
        """Define qual fonte de dados está selecionada na UI."""
        self._selected_source_path = source_id

    def update_selected_source_association(self, assoc_type: str):
        """Atualiza o tipo de associação (global/local) da fonte selecionada."""
        if not self._selected_source_path:
            logging.warning("AppState: Tentativa de atualizar associação sem fonte selecionada.")
            return
            
        source = self.get_data_source_by_id(self._selected_source_path)
        if source:
            source.association_type = assoc_type
            logging.info(f"AppState: Associação de '{source.name}' definida para '{assoc_type}'.")
            
            # Emite o sinal
            self.data_association_changed.emit(source.path, source.association_type)