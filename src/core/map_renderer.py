import logging
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGraphicsItem 

from ui.map.map_view import MapView
from src.domain.app_state import AppState
from src.utils.config import ConfigManager


class MapRenderer:
    """
    Responsabilidade única: Desenhar o mapa (Nós e Arestas)
    na MapView (QGraphicsScene).
    (Modificado para usar Canetas Cosméticas nas arestas)
    """

    def __init__(
        self,
        map_view: MapView,
        app_state: AppState,
        config: ConfigManager,
    ):
        self._view = map_view
        self._scene = map_view.scene 
        self._app_state = app_state

        self._drawable_items_by_id: dict[str, list[QGraphicsItem]] = {}
        self._current_highlight: list[QGraphicsItem] = []
        
        self._zoom_config = config.get("map_zoom", {})
        self._min_zoom = self._zoom_config.get("min", 0.1)
        self._max_zoom = self._zoom_config.get("max", 10.0)

        self._colors = config.get("map_colors", {})
        self._edge_color = QColor(self._colors.get("edge", "#4A4A4A"))
        self._node_color = QColor(self._colors.get("node", "#E74C3C"))
        
        self._sel_assoc_color = QColor(self._colors.get("selection_associated", "#E74C3C")) 
        self._sel_free_color = QColor(self._colors.get("selection_free", "#2ECC71")) 

        bg_color = self._colors.get("background", "#FFFFFF")
        self._scene.setBackgroundBrush(QColor(bg_color))

        # --- 1. ALTERAÇÃO PRINCIPAL (Canetas Cosméticas) ---
        
        # Aresta (Rua) - COSMÉTICA (largura constante em pixels)
        # (Largura base 2px, cantos arredondados)
        pen_edge = QPen(self._edge_color, 2, Qt.SolidLine, Qt.RoundCap)
        pen_edge.setCosmetic(True)

        # Aresta Associada (Vermelha) - COSMÉTICA (4px)
        pen_edge_assoc = QPen(self._sel_assoc_color, 4, Qt.SolidLine, Qt.RoundCap)
        pen_edge_assoc.setCosmetic(True)

        # Aresta Livre (Verde) - COSMÉTICA (4px)
        pen_edge_free = QPen(self._sel_free_color, 4, Qt.SolidLine, Qt.RoundCap)
        pen_edge_free.setCosmetic(True)

        # --- Canetas NÃO-COSMÉTICAS (escalam com o zoom) ---
        
        # Nó (Interseção) - NÃO COSMÉTICA
        pen_node = QPen(self._node_color, 1, Qt.SolidLine)

        # Nó Associado (Vermelho) - NÃO COSMÉTICA
        pen_node_assoc = QPen(self._sel_assoc_color, 2, Qt.SolidLine)

        # Nó Livre (Verde) - NÃO COSMÉTICA
        pen_node_free = QPen(self._sel_free_color, 2, Qt.SolidLine)

        self._pens = {
            "edge": pen_edge,
            "node": pen_node,
            "selected_edge_assoc": pen_edge_assoc,
            "selected_node_assoc": pen_node_assoc,
            "selected_edge_free": pen_edge_free,
            "selected_node_free": pen_node_free
        }

        # --- Pincéis (Brushes) ---
        self._brushes = {
            "node": QBrush(self._node_color),
            "selected_node_assoc": QBrush(self._sel_assoc_color),
            "selected_node_free": QBrush(self._sel_free_color)
        }
        # --- FIM DA ALTERAÇÃO ---

    def draw_map(self):
        """Lê os dados do AppState e desenha o mapa na cena."""
        logging.info("MapRenderer: Reading map data from AppState...")
        self._scene.clear()
        
        self._drawable_items_by_id.clear()
        self._current_highlight.clear()
        
        nodes = self._app_state.get_all_nodes()
        edges = self._app_state.get_all_edges()

        if not nodes and not edges:
            logging.warning("MapRenderer: No map data to draw.")
            return

        for edge in edges:
            self._draw_edge(edge)

        node_count = 0
        for node in nodes:
            if node.node_type == "internal":
                continue
            self._draw_node(node)
            node_count += 1
        
        logging.info(f"MapRenderer: Map drawn. {node_count} nodes, {len(edges)} edges.")

        self._view.fit_map_in_view()
        self._view.set_zoom_limits(self._min_zoom, self._max_zoom)


    def _draw_edge(self, edge):
        """Desenha uma única aresta (rua) na cena."""
        pen = self._pens["edge"]
        for i in range(len(edge.shape) - 1):
            p1 = edge.shape[i]
            p2 = edge.shape[i + 1]
            line = self._scene.addLine(p1[0], -p1[1], p2[0], -p2[1], pen)
            line.setData(0, "edge")
            line.setData(1, edge.id)
            line.setZValue(0)
            self._drawable_items_by_id.setdefault(edge.id, []).append(line)

    def _draw_node(self, node):
        """Desenha um único nó (interseção) na cena."""
        pen = self._pens["node"]
        brush = self._brushes["node"]
        
        r = 5 # Raio em coordenadas do mundo (escala com o zoom)
        ellipse = self._scene.addEllipse(-r, -r, 2 * r, 2 * r, pen, brush)
        ellipse.setPos(node.x, -node.y)
        ellipse.setData(0, "node")
        ellipse.setData(1, node.id)
        ellipse.setZValue(1)
        self._drawable_items_by_id[node.id] = [ellipse]

    # --- Método de Destaque (Modificado) ---

    @Slot(str, bool)
    def highlight_element(self, element_id: str | None, is_associated: bool):
        """
        Destaca um elemento (Nó ou Aresta) pelo seu ID.
        
        :param element_id: O ID do elemento a destacar.
        :param is_associated: True (Vermelho) se já tiver dados, False (Verde) se livre.
        """
        self.clear_highlight()
        
        if not element_id:
            return

        items_to_highlight = self._drawable_items_by_id.get(element_id)
        if not items_to_highlight:
            logging.warning(f"MapRenderer: Não foi possível encontrar o item '{element_id}' para destacar.")
            return

        color_key = "assoc" if is_associated else "free"

        for item in items_to_highlight:
            item_type = item.data(0)
            
            if item_type == "node":
                item.setPen(self._pens[f"selected_node_{color_key}"])
                item.setBrush(self._brushes[f"selected_node_{color_key}"])
                item.setZValue(2) 
            
            elif item_type == "edge":
                item.setPen(self._pens[f"selected_edge_{color_key}"])
                item.setZValue(1) 
        
        self._current_highlight = items_to_highlight

    @Slot()
    def clear_highlight(self):
        """Restaura os itens destacados de volta à sua aparência normal."""
        if not self._current_highlight:
            return

        for item in self._current_highlight:
            item_type = item.data(0)
            
            if item_type == "node":
                item.setPen(self._pens["node"])
                item.setBrush(self._brushes["node"])
                item.setZValue(1)
            
            elif item_type == "edge":
                item.setPen(self._pens["edge"])
                item.setZValue(0)
        
        self._current_highlight.clear()