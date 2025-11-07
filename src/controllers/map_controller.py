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

# File: src/controllers/map_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Map View specialist (Controller). Connects the MapView (View) signals
#    to the application logic (Model). Handles rendering the map,
#    pan/zoom, and node selection.

from PySide6.QtCore import QObject, Slot, Qt, QPoint # FIX: Imported QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QAction
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QMenu

# Import the View
from ui.map.map_view import MapView

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import MapNode, MapEdge

# Need a type hint for the SourcesController, but don't import it
# to avoid a circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.controllers.sources_controller import SourcesController


class MapController(QObject):
    """
    Controller for the Map View.
    """
    
    # --- Constants for map styling ---
    NODE_RADIUS = 5
    NODE_BRUSH = QBrush(QColor("#3498db")) # Blue
    NODE_PEN = QPen(QColor("#2980b9"), 1.5) # Darker Blue
    
    EDGE_PEN = QPen(QColor("#95a5a6"), 1) # Gray
    
    NODE_HIGHLIGHT_BRUSH = QBrush(QColor("#e74c3c")) # Red
    NODE_HIGHLIGHT_PEN = QPen(QColor("#c0392b"), 2) # Darker Red
    # --- End Constants ---
    
    
    def __init__(self, view: MapView, app_state: AppState, parent=None):
        """
        Controller constructor.
        
        Args:
            view (MapView): The view instance for the map.
            app_state (AppState): The shared application state (Model).
        """
        super().__init__(parent)
        
        self.view = view
        self.app_state = app_state
        self.sources_controller: 'SourcesController' = None # Set by MainController
        
        self._translator = None
        self._node_items = {} # Cache: {node_id: QGraphicsEllipseItem}
        
        # State for node selection
        self._is_selecting_node = False
        self._selection_source_id = None
        
        self._setup_context_menu()
        self._connect_signals()

    def set_sources_controller(self, sources_controller: 'SourcesController'):
        """
        Sets the reference to the SourcesController for cross-communication.
        """
        self.sources_controller = sources_controller

    def translate_ui(self, translator):
        """
        Applies translations to the view components.
        
        Args:
            translator (callable): The i18n_frontend.t function.
        """
        self._translator = translator
        try:
            self._context_menu.setTitle(translator("map_view.context_menu.title"))
            self._fit_zoom_action.setText(translator("map_view.context_menu.fit_zoom"))
            self._clear_selection_action.setText(translator("map_view.context_menu.clear_selection"))
        except Exception as e:
            print(f"Error applying translations in MapController: {e}")

    def _setup_context_menu(self):
        """ Creates the right-click context menu for the map view. """
        self._context_menu = QMenu()
        
        self._fit_zoom_action = QAction("Fit View to Map")
        self._fit_zoom_action.triggered.connect(self._on_fit_zoom)
        
        self._clear_selection_action = QAction("Clear Selection")
        self._clear_selection_action.triggered.connect(self._on_clear_selection)
        
        self._context_menu.addAction(self._fit_zoom_action)
        self._context_menu.addAction(self._clear_selection_action)
        
    def _connect_signals(self):
        """ Connects view signals to controller slots. """
        # Custom signal from MapView (View)
        self.view.nodeClicked.connect(self._on_node_clicked)
        # Custom signal from MapView (View)
        self.view.emptySpaceClicked.connect(self._on_empty_space_clicked)
        # Custom signal from MapView (View)
        self.view.customContextMenuRequested.connect(self._on_context_menu)
        
    def draw_map(self):
        """
        Reads the map data from the AppState (Model) and commands the
        MapView (View) to render it.
        """
        print("MapController: Reading map data from AppState...")
        map_data = self.app_state.get_map_data()
        if not map_data:
            print("MapController: No map data found.")
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
            self.view.add_item_to_scene(path_item)

        # --- 3. Draw Nodes (Circles) ---
        r = self.NODE_RADIUS # Alias for radius
        for node in nodes:
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
            
        print(f"MapController: Map drawn. {len(nodes)} nodes, {len(edges)} edges.")
        
        # --- 4. Fit zoom ---
        self._on_fit_zoom()

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

    def start_node_selection(self, source_id: str):
        """
        Enters "node selection" mode. The next node click will be
        captured to associate with the given source_id.
        """
        self._is_selecting_node = True
        self._selection_source_id = source_id
        
        # 1. Update View (Cursor)
        self.view.setCursor(Qt.CrossCursor)
        
        # 2. Notify SourcesController to update status label
        if self.sources_controller:
            self.sources_controller.notify_node_selection_mode(source_id, True)

    def cancel_node_selection(self):
        """ Exits "node selection" mode. """
        if not self._is_selecting_node:
            return
            
        source_id = self._selection_source_id
        
        self._is_selecting_node = False
        self._selection_source_id = None
        
        # 1. Update View (Cursor)
        self.view.setCursor(Qt.ArrowCursor)
        
        # 2. Notify SourcesController to update status label
        if self.sources_controller:
            self.sources_controller.notify_node_selection_mode(source_id, False)

    # --- SLOTS ---

    @Slot(str)
    def _on_node_clicked(self, node_id: str):
        """
        Slot triggered by the View when a node item is clicked.
        """
        print(f"MapController: Node '{node_id}' clicked.")
        
        if self._is_selecting_node:
            # --- We are in "selection" mode ---
            
            source_id = self._selection_source_id
            
            # 1. Update the Model (AppState)
            source = self.app_state.get_source_by_id(source_id)
            if source:
                source.associated_node_id = node_id
                print(f"MapController: Associated Source '{source_id}' with Node '{node_id}'.")

            # 2. Update View (Map Highlight)
            self.highlight_node(node_id)
            
            # 3. Exit selection mode
            self.cancel_node_selection()
            
            # 4. Notify SourcesController to update its details panel
            if self.sources_controller:
                self.sources_controller.refresh_details(source_id)
                
        else:
            # --- We are in "normal" mode ---
            
            # 1. Update View (Map Highlight)
            self.highlight_node(node_id)
            
            # 2. TODO: Check if any sources are associated with this node
            # and update the SourcesPanel list? (Future feature)

    @Slot()
    def _on_empty_space_clicked(self):
        """
        Slot triggered by the View when empty space is clicked.
        """
        if self._is_selecting_node:
            # Cancel selection mode if user clicks away
            self.cancel_node_selection()
        
        self._on_clear_selection()
        
    @Slot()
    def _on_clear_selection(self):
        """ Clears the highlighted node. """
        # 1. Update View (Map Highlight)
        self.clear_selection_highlight()
        
        # 2. TODO: Clear selection in SourcesPanel list? (Future feature)

    @Slot(QPoint)
    def _on_context_menu(self, pos):
        """
        Slot triggered by the View on right-click.
        """
        # Show the context menu at the cursor's global position
        self.view.show_context_menu(self._context_menu, pos)
        
    @Slot()
    def _on_fit_zoom(self):
        """
        Commands the View to fit the entire scene in the viewport.
        """
        self.view.fit_to_scene()