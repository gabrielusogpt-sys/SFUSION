import logging
from PySide6.QtCore import QObject, Slot

from src.domain.app_state import AppState
from src.core.map_renderer import MapRenderer
from src.controllers.info_controller import InfoController  # <--- 1. Importar
from ui.map.map_view import MapView


class MapController(QObject):
    """
    Controlador para o mapa. Gere interações de clique
    e delega o desenho e a exibição de informações.
    (Refatorado para SRP)
    """

    def __init__(
        self,
        app_state: AppState,
        map_renderer: MapRenderer,
        info_controller: InfoController,  # <--- 2. Aceitar o InfoController
    ):
        super().__init__()
        self._app_state = app_state
        self._map_renderer = map_renderer
        self._info_controller = info_controller  # <--- 3. Armazenar a referência

    def setup_connections(self, map_view: MapView):
        """Conecta os sinais da MapView aos slots deste controlador."""
        map_view.nodeClicked.connect(self._on_node_clicked)
        map_view.edgeClicked.connect(self._on_edge_clicked)
        map_view.emptySpaceClicked.connect(self._on_empty_space_clicked)

        # Conecta o estado da aplicação ao renderer
        self._app_state.map_data_loaded.connect(self.draw_map)

    @Slot(str)
    def _on_node_clicked(self, node_id: str):
        """Chamado quando um nó (QGraphicsItem) é clicado."""
        logging.info(f"MapController: Node '{node_id}' clicked.")
        node = self._app_state.get_node_by_id(node_id)
        if node:
            # 4. Usar o InfoController para mostrar os dados do nó
            self._info_controller.show_for_node(node)
        else:
            logging.warning(f"MapController: Node ID '{node_id}' not found in AppState.")

    @Slot(str)
    def _on_edge_clicked(self, edge_id: str):
        """Chamado quando uma aresta (QGraphicsItem) é clicada."""
        logging.info(f"MapController: Edge '{edge_id}' clicked.")
        edge = self._app_state.get_edge_by_id(edge_id)
        if edge:
            # 5. Usar o InfoController para mostrar os dados da aresta
            self._info_controller.show_for_edge(edge)
        else:
            logging.warning(f"MapController: Edge ID '{edge_id}' not found in AppState.")

    @Slot()
    def _on_empty_space_clicked(self):
        """Chamado quando um espaço vazio no mapa é clicado."""
        logging.info("MapController: Empty space clicked.")
        # Esconde o painel de informações se estiver visível
        self._info_controller.hide_panel()

    @Slot()
    def draw_map(self):
        """
        Delega a renderização do mapa ao MapRenderer.
        Este slot é conectado ao sinal map_data_loaded do AppState.
        """
        logging.info("MapController: Delegating 'draw_map' to MapRenderer.")
        self._map_renderer.draw_map()   