import logging
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt

from ui.map.map_view import MapView
from src.domain.app_state import AppState
from src.utils.config import ConfigManager


class MapRenderer:
    """
    Responsabilidade única: Desenhar o mapa (Nós e Arestas)
    na MapView (QGraphicsScene).
    (Refatorado do MapController)
    """

    def __init__(
        self,
        map_view: MapView,
        app_state: AppState,
        config: ConfigManager,
    ):
        self._view = map_view
        
        # --- CORREÇÃO PRINCIPAL AQUI ---
        # A 'scene' na MapView é um atributo (self.scene), não um método (self.scene()).
        # Removemos os parênteses ()
        self._scene = map_view.scene 
        # --- FIM DA CORREÇÃO ---

        self._app_state = app_state

        # Configurações de renderização
        self._zoom_config = config.get("map_zoom", {})
        self._min_zoom = self._zoom_config.get("min", 0.1)
        self._max_zoom = self._zoom_config.get("max", 10.0)

        self._colors = config.get("map_colors", {})
        self._edge_color = QColor(self._colors.get("edge", "#000000"))
        self._node_color = QColor(self._colors.get("node", "#FF0000"))
        self._internal_node_color = QColor(
            self._colors.get("internal_node", "#AAAAAA")
        )
        
        # Cor de fundo da cena (lida do config)
        bg_color = self._colors.get("background", "#FFFFFF")
        self._scene.setBackgroundBrush(QColor(bg_color))

        self._pens = {
            "edge": QPen(self._edge_color, 4, Qt.SolidLine),
            "node": QPen(self._node_color, 1, Qt.SolidLine),
            "internal_node": QPen(self._internal_node_color, 1, Qt.SolidLine),
        }
        self._brushes = {
            "node": QBrush(self._node_color),
            "internal_node": QBrush(self._internal_node_color),
        }

    def draw_map(self):
        """Lê os dados do AppState e desenha o mapa na cena."""
        logging.info("MapRenderer: Reading map data from AppState...")
        self._scene.clear()
        nodes = self._app_state.get_all_nodes()
        edges = self._app_state.get_all_edges()

        if not nodes and not edges:
            logging.warning("MapRenderer: No map data to draw.")
            return

        # 1. Desenhar Arestas (Ruas)
        for edge in edges:
            self._draw_edge(edge)

        # 2. Desenhar Nós (Interseções)
        node_count = 0
        for node in nodes:
            # Filtrar e não desenhar nós do tipo "internal"
            if node.node_type == "internal":
                continue
            self._draw_node(node)
            node_count += 1
        
        logging.info(f"MapRenderer: Map drawn. {node_count} nodes, {len(edges)} edges.")

        # Ajustar a vista para caber o mapa
        self._view.fit_map_in_view()
        self._view.set_zoom_limits(self._min_zoom, self._max_zoom)


    def _draw_edge(self, edge):
        """Desenha uma única aresta (rua) na cena."""
        pen = self._pens["edge"]
        for i in range(len(edge.shape) - 1):
            p1 = edge.shape[i]
            p2 = edge.shape[i + 1]
            line = self._scene.addLine(p1[0], -p1[1], p2[0], -p2[1], pen)
            line.setData(0, "edge")  # Identificador de tipo
            line.setData(1, edge.id) # ID do elemento
            line.setZValue(0)  # Arestas ficam no fundo

    def _draw_node(self, node):
        """Desenha um único nó (interseção) na cena."""
        pen = self._pens["node"]
        brush = self._brushes["node"]
        
        r = 5  # Raio do nó
        ellipse = self._scene.addEllipse(-r, -r, 2 * r, 2 * r, pen, brush)
        ellipse.setPos(node.x, -node.y)
        ellipse.setData(0, "node")  # Identificador de tipo
        ellipse.setData(1, node.id) # ID do elemento
        ellipse.setZValue(1)  # Nós ficam por cima das arestas