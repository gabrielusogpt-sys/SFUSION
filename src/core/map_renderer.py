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

# File: src/core/map_renderer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Map Renderer (SRP Refactor).
#    Handles the "Rendering" responsibility: drawing items, styling,
#    and highlighting. It is the "Painter" commanded by the MapController.

from PySide6.QtCore import QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem

# Import the View
from ui.map.map_view import MapView

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import MapEdge


class MapRenderer(QObject):
    """
    Handles all rendering logic for the MapView.
    This is the "Painter" half of the original MapController.
    """
    
    # --- Constants for map styling ---
    NODE_RADIUS = 5
    NODE_BRUSH = QBrush(QColor("#3498db")) # Blue
    NODE_PEN = QPen(QColor("#2980b9"), 1.5) # Darker Blue
    
    # --- FIX (Problem 1): Make streets thicker ---
    EDGE_PEN = QPen(QColor("#95a5a6"), 4) # Gray, Width 4
    # --- END FIX ---
    
    NODE_HIGHLIGHT_BRUSH = QBrush(QColor("#e74c3c")) # Red
    NODE_HIGHLIGHT_PEN = QPen(QColor("#c0392b"), 2) # Darker Red
    # --- End Constants ---
    
    
    def __init__(self, view: MapView, app_state: AppState, parent=None):
        """
        Renderer constructor.
        
        Args:
            view (MapView): The view instance for the map.
            app_state (AppState): The shared application state (Model).
        """
        super().__init__(parent)
        
        self.view = view
        self.app_state = app_state
        
        self._node_items = {} # Cache: {node_id: QGraphicsEllipseItem}
        print("MapRenderer: Initialized.")

    def draw_map(self):
        """
        Reads the map data from the AppState (Model) and commands the
        MapView (View) to render it.
        """
        print("MapRenderer: Reading map data from AppState...")
        map_data = self.app_state.get_map_data()
        if not map_data:
            print("MapRenderer: No map data found.")
            return

        nodes = map_data.get("nodes", [])
        edges = map_data.get("edges", [])

        # --- 1. Clear old map ---
        self.view.clear_scene()
        self._node_items.clear()
        
        # --- 2. Draw Edges (Lines) ---
        # Edges are drawn first so they appear "under" the nodes
        for edge in edges:
            path = self._create_edge_path(edge)
            path_item = QGraphicsPathItem(path)
            path_item.setPen(self.EDGE_PEN)
            
            # --- FIX (Req 3): Store the edge ID on the item ---
            # We use key 1 for edges (key 0 is for nodes)
            path_item.setData(1, edge.id)
            # --- END FIX ---
            
            self.view.add_item_to_scene(path_item)

        # --- 3. Draw Nodes (Circles) ---
        r = self.NODE_RADIUS # Alias for radius
        for node in nodes:
        
            # --- FIX (Problem 2): Filter "internal" nodes ---
            # Do not draw the internal geometry nodes, only "real" junctions.
            if node.node_type == "internal":
                continue
            # --- END FIX ---

            # Create a QGraphicsEllipseItem
            # (x, y, width, height)
            node_item = QGraphicsEllipseItem(node.x - r, node.y - r, r*2, r*2)
            
            # Store the node ID inside the item for later retrieval
            node_item.setData(0, node.id)
            
            node_item.setBrush(self.NODE_BRUSH)
            node_item.setPen(self.NODE_PEN)
            node_item.setZValue(1) # Ensure nodes are drawn on top of edges
            
            # Add to scene
            self.view.add_item_to_scene(node_item)
            
            # Add to cache for highlighting
            self._node_items[node.id] = node_item
            
        print(f"MapRenderer: Map drawn. {len(nodes)} nodes, {len(edges)} edges.")
        
        # --- 4. Fit zoom ---
        # Note: The controller is responsible for the *decision*
        # to fit zoom. We just draw.
        self.view.fit_to_scene()

    def _create_edge_path(self, edge: MapEdge) -> QPainterPath:
        """
        Creates a QPainterPath (a line or curve) from an edge's shape.
        """
        path = QPainterPath()
        
        if not edge.shape:
            # If no shape, draw a straight line between nodes
            start_node = self.app_state.get_node_by_id(edge.from_node)
            end_node = self.app_state.get_node_by_id(edge.to_node)
            if start_node and end_node:
                path.moveTo(start_node.x, start_node.y)
                path.lineTo(end_node.x, end_node.y)
        else:
            # If shape is defined (list of (x,y) tuples), use it
            start_point = edge.shape[0]
            path.moveTo(start_point[0], start_point[1])
            for point in edge.shape[1:]:
                path.lineTo(point[0], point[1])
                
        return path

    def highlight_node(self, node_id: str | None):
        """
        Highlights a specific node and de-highlights all others.
        
        Args:
            node_id (str | None): The ID of the node to highlight.
                                  If None, clears all highlights.
        """
        # 1. De-highlight all nodes
        for item in self._node_items.values():
            item.setBrush(self.NODE_BRUSH)
            item.setPen(self.NODE_PEN)
            
        # 2. Highlight the specific node
        if node_id and node_id in self._node_items:
            item = self._node_items[node_id]
            item.setBrush(self.NODE_HIGHLIGHT_BRUSH)
            item.setPen(self.NODE_HIGHLIGHT_PEN)

    def clear_selection_highlight(self):
        """ Resets all nodes to their default appearance. """
        self.highlight_node(None)