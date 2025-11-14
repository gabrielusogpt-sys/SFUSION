import logging
from PySide6.QtCore import QObject, Slot, Qt

from src.domain.app_state import AppState
from src.core.map_renderer import MapRenderer
from src.controllers.info_controller import InfoController
from ui.map.map_view import MapView


class MapController(QObject):
    """
    Controlador para o mapa. Gere interações de clique
    e delega o desenho e a exibição de informações.
    (Modificado para atualizar a áurea após o salvamento)
    """

    def __init__(
        self,
        app_state: AppState,
        map_renderer: MapRenderer,
        info_controller: InfoController,
    ):
        super().__init__()
        self._app_state = app_state
        self._map_renderer = map_renderer
        self._info_controller = info_controller
        self._map_view = None
        
        # 1. Manter o ID do elemento selecionado
        self._current_selected_element_id: str | None = None

    def setup_connections(self, map_view: MapView):
        """Conecta os sinais da MapView aos slots deste controlador."""
        self._map_view = map_view
        
        map_view.nodeClicked.connect(self._on_node_clicked)
        map_view.edgeClicked.connect(self._on_edge_clicked)
        map_view.emptySpaceClicked.connect(self._on_empty_space_clicked)

        self._app_state.map_data_loaded.connect(self.draw_map)
        self._app_state.association_mode_changed.connect(
            self._on_association_mode_changed
        )
        
        # --- 2. NOVA CONEXÃO (Corrigir Bug 2) ---
        # Ouvir o sinal de que uma associação mudou
        self._app_state.data_association_changed.connect(
            self._on_association_updated
        )

    # --- Lógica de Clique Atualizada ---

    @Slot(str)
    def _on_node_clicked(self, node_id: str):
        """Chamado quando um nó (QGraphicsItem) é clicado."""
        
        if self._app_state.is_in_association_mode():
            logging.info(f"MapController: Associando fonte ao Nó '{node_id}'.")
            self._app_state.associate_selected_source_to_element(node_id)
        
        else:
            # 3. Armazena o ID selecionado
            self._current_selected_element_id = node_id
            
            source = self._app_state.get_source_associated_with_element(node_id)
            is_associated = (source is not None)
            
            self._map_renderer.highlight_element(node_id, is_associated)

            logging.info(f"MapController: Exibindo editor para o Nó '{node_id}'.")
            node = self._app_state.get_node_by_id(node_id)
            if node:
                self._info_controller.show_for_node(node)
            else:
                logging.warning(f"MapController: Node ID '{node_id}' not found in AppState.")

    @Slot(str)
    def _on_edge_clicked(self, edge_id: str):
        """Chamado quando uma aresta (QGraphicsItem) é clicada."""
        
        if self._app_state.is_in_association_mode():
            logging.info(f"MapController: Associando fonte à Aresta '{edge_id}'.")
            self._app_state.associate_selected_source_to_element(edge_id)
            
        else:
            # 3. Armazena o ID selecionado
            self._current_selected_element_id = edge_id
            
            source = self._app_state.get_source_associated_with_element(edge_id)
            is_associated = (source is not None)

            self._map_renderer.highlight_element(edge_id, is_associated)

            logging.info(f"MapController: Exibindo editor para a Aresta '{edge_id}'.")
            edge = self._app_state.get_edge_by_id(edge_id)
            if edge:
                self._info_controller.show_for_edge(edge)
            else:
                logging.warning(f"MapController: Edge ID '{edge_id}' not found in AppState.")

    @Slot()
    def _on_empty_space_clicked(self):
        """Chamado quando um espaço vazio no mapa é clicado."""
        logging.info("MapController: Empty space clicked.")
        
        # 3. Limpa o ID selecionado
        self._current_selected_element_id = None
        
        self._info_controller.hide_panel()
        self._app_state.exit_association_mode()

    # --- Slots (Ouvem o Modelo) ---

    @Slot(bool)
    def _on_association_mode_changed(self, is_active: bool):
        """Chamado pelo AppState. Altera o cursor do mapa."""
        if not self._map_view:
            return
        if is_active:
            self._map_view.setCursor(Qt.CrossCursor)
        else:
            self._map_view.setCursor(Qt.ArrowCursor)

    # --- 4. NOVO SLOT (Corrigir Bug 2) ---
    @Slot(str, str)
    def _on_association_updated(self, source_id: str, element_or_type: str):
        """
        Chamado pelo AppState quando uma associação muda.
        Atualiza a áurea se o elemento afetado for o selecionado.
        """
        # Se o elemento que acabou de ser atualizado é o que está
        # selecionado atualmente, atualizamos a sua cor.
        if element_or_type == self._current_selected_element_id:
            logging.debug(f"MapController: Atualizando áurea para o elemento {element_or_type}.")
            
            # Re-verifica o estado de associação
            source = self._app_state.get_source_associated_with_element(element_or_type)
            is_associated = (source is not None)
            
            # Re-aplica o destaque (que agora será Vermelho)
            self._map_renderer.highlight_element(element_or_type, is_associated)

    @Slot()
    def draw_map(self):
        """
        Delega a renderização do mapa ao MapRenderer.
        """
        logging.info("MapController: Delegating 'draw_map' to MapRenderer.")
        self._map_renderer.draw_map()