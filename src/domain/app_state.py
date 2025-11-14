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

# File: src/domain/app_state.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    AppState (Model). A "Fonte Única da Verdade" (Single Source of Truth)
#    para o estado da aplicação.

import logging
from PySide6.QtCore import QObject, Signal 
from .entities import MapNode, MapEdge, DataSource, AssociationType


class AppState(QObject):
    """
    Armazena o estado atual da aplicação na memória.
    Atua como a "Fonte Única da Verdade".
    Emite sinais quando os dados são alterados.
    """
    
    map_data_loaded = Signal()
    data_sources_changed = Signal(list) 
    # Emite (source_id: str, novo_dado: any [tipo ou id_elemento])
    data_association_changed = Signal(str, str)
    association_mode_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        
        self._nodes: list[MapNode] = []
        self._edges: list[MapEdge] = []
        self._nodes_by_id: dict[str, MapNode] = {}
        self._edges_by_id: dict[str, MapEdge] = {}

        self._data_sources: list[DataSource] = []
        self._sources_by_path: dict[str, DataSource] = {}
        
        self._selected_source_path: str | None = None
        self._is_in_association_mode: bool = False

    # --- Métodos de Mapa ---

    def set_map_data(self, nodes: list[MapNode], edges: list[MapEdge]):
        self._nodes = nodes
        self._edges = edges
        self._nodes_by_id = {node.id: node for node in nodes}
        self._edges_by_id = {edge.id: edge for edge in edges}
        logging.info(f"AppState: Dados do mapa atualizados. {len(nodes)} nós, {len(edges)} arestas.")
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
        element = self.get_node_by_id(element_id) or self.get_edge_by_id(element_id)
        if element:
            element.real_name = real_name if real_name else None
            logging.info(f"AppState: 'real_name' atualizado para '{element_id}'")
        else:
            logging.warning(f"AppState: Tentativa de atualizar nome de elemento desconhecido: '{element_id}'")

    # --- Métodos de Fonte de Dados ---

    def add_data_source(self, source: DataSource):
        if source.path in self._sources_by_path:
            logging.warning(f"AppState: Fonte de dados '{source.path}' já existe.")
            return
        self._data_sources.append(source)
        self._sources_by_path[source.path] = source
        self.data_sources_changed.emit(self._data_sources)

    def get_all_data_sources(self) -> list[DataSource]:
        return self._data_sources

    def get_data_source_by_id(self, source_id: str) -> DataSource | None:
        return self._sources_by_path.get(source_id)

    def set_selected_data_source(self, source_id: str | None):
        self._selected_source_path = source_id
        if not source_id:
            self.exit_association_mode()

    def update_selected_source_association_type(self, assoc_type: str):
        """Atualiza o TIPO (global/local) da fonte selecionada."""
        source = self._get_selected_source()
        if source:
            try:
                source.association_type = AssociationType(assoc_type.upper())
                # Limpa associação de elemento se mudar de tipo
                source.associated_element_id = None
                
                logging.info(f"AppState: Associação de '{source.name}' definida para '{assoc_type}'.")
                self.data_association_changed.emit(source.path, source.association_type.value)
            except ValueError:
                logging.error(f"AppState: Tentativa de definir tipo inválido: {assoc_type}")

    # --- Lógica de Modo de Associação (Clique no Mapa) ---
    
    def _get_selected_source(self) -> DataSource | None:
        if not self._selected_source_path:
            return None
        return self.get_data_source_by_id(self._selected_source_path)

    def is_in_association_mode(self) -> bool:
        return self._is_in_association_mode

    def enter_association_mode(self):
        """Ativa o modo de associação (via painel direito)."""
        if self._is_in_association_mode:
            return
        if not self._selected_source_path:
            logging.warning("AppState: Tentativa de entrar em modo de associação sem fonte selecionada.")
            return
            
        # 1. MUDANÇA DE LÓGICA: Verifica se a fonte já está em uso
        source = self._get_selected_source()
        if source and source.associated_element_id:
            logging.warning(f"AppState: Fonte '{source.name}' já associada. Cancele a associação primeiro.")
            self.set_selected_data_source(None) # Limpa a seleção
            return

        self._is_in_association_mode = True
        self.association_mode_changed.emit(True)
        logging.info("AppState: Modo de associação ATIVADO.")

    def exit_association_mode(self):
        if not self._is_in_association_mode:
            return
        self._is_in_association_mode = False
        self.association_mode_changed.emit(False)
        logging.info("AppState: Modo de associação DESATIVADO.")

    def associate_selected_source_to_element(self, element_id: str):
        """Associa a fonte selecionada (via Painel Direito) a um nó/aresta."""
        source = self._get_selected_source()
        if not source:
            logging.error("AppState: Tentativa de associar, mas nenhuma fonte estava selecionada.")
            self.exit_association_mode()
            return
        
        if source.associated_element_id:
            logging.warning(f"AppState: Fonte '{source.name}' já estava associada. Ignorando.")
            self.exit_association_mode()
            return
            
        source.associated_element_id = element_id
        source.association_type = AssociationType.LOCAL 
        
        logging.info(f"AppState: Fonte '{source.name}' associada ao elemento '{element_id}'.")
        self.data_association_changed.emit(source.path, element_id)
        self.exit_association_mode()

    # --- Métodos de Gestão de Fontes (Menu Direito) ---

    def delete_data_source(self, source_id: str):
        source = self._sources_by_path.get(source_id)
        if not source:
            logging.warning(f"AppState: Tentativa de deletar fonte desconhecida: {source_id}")
            return

        self._data_sources.remove(source)
        del self._sources_by_path[source_id]
        logging.info(f"AppState: Fonte de dados '{source.name}' removida.")

        if self._selected_source_path == source_id:
            self.set_selected_data_source(None)
        self.data_sources_changed.emit(self._data_sources)

    def toggle_source_association_type(self, source_id: str):
        source = self.get_data_source_by_id(source_id)
        if not source:
            return

        if source.association_type == AssociationType.GLOBAL:
            source.association_type = AssociationType.LOCAL
        else:
            source.association_type = AssociationType.GLOBAL
        
        source.associated_element_id = None
        logging.info(f"AppState: Associação de '{source.name}' alterada para '{source.association_type.value}'.")
        self.data_association_changed.emit(source.path, source.association_type.value)

    # --- 2. MÉTODOS MODIFICADOS (Para o EditorPanel / Painel Esquerdo) ---

    def get_sources_associated_with_element(self, element_id: str) -> list[DataSource]:
        """(MODIFICADO) Retorna TODAS as fontes de dados associadas a este elemento."""
        sources = []
        for source in self._data_sources:
            if source.associated_element_id == element_id:
                sources.append(source)
        return sources

    def get_available_local_sources(self, current_element_id: str) -> list[DataSource]:
        """
        Retorna fontes locais que estão livres (ou já associadas a este elemento).
        """
        available = []
        for source in self._data_sources:
            # Só mostra fontes marcadas como LOCAL
            if source.association_type == AssociationType.LOCAL:
                # Se não tem associação OU se a associação é com o elemento atual
                if source.associated_element_id is None or source.associated_element_id == current_element_id:
                    available.append(source)
        return available

    def set_element_associations(self, element_id: str, new_source_ids: list[str]):
        """
        (MODIFICADO) Define as associações via Checkbox do Editor.
        Recebe a lista COMPLETA de IDs que devem estar associados.
        """
        
        new_ids_set = set(new_source_ids)
        
        # 1. Obter associações atuais *deste elemento*
        current_sources = self.get_sources_associated_with_element(element_id)
        current_ids_set = {s.path for s in current_sources}

        # 2. Calcular diferenças
        ids_to_add = new_ids_set - current_ids_set
        ids_to_remove = current_ids_set - new_ids_set
        
        # 3. Remover associações antigas (desmarcadas)
        for source_id in ids_to_remove:
            source = self.get_data_source_by_id(source_id)
            if source:
                source.associated_element_id = None
                logging.info(f"AppState: Fonte '{source.name}' libertada de '{element_id}'.")
                # Avisa a UI que a fonte agora é 'LOCAL' (mas não associada)
                self.data_association_changed.emit(source.path, "LOCAL") 
        
        # 4. Adicionar novas associações (marcadas)
        for source_id in ids_to_add:
            source = self.get_data_source_by_id(source_id)
            if source:
                # Segurança: Se a fonte já pertencia a outro, removemos de lá
                if source.associated_element_id and source.associated_element_id != element_id:
                    logging.warning(f"AppState: Fonte '{source.name}' movida de '{source.associated_element_id}' para '{element_id}'.")
                    # (Precisamos de encontrar o elemento antigo e atualizar a sua cor?)
                    # (Por agora, apenas a nova associação é emitida)
                
                source.associated_element_id = element_id
                source.association_type = AssociationType.LOCAL # Garante
                
                logging.info(f"AppState: Fonte '{source.name}' associada a '{element_id}' (via Editor).")
                self.data_association_changed.emit(source.path, element_id)