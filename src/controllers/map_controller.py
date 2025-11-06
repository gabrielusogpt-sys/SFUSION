# SFusion (SYNAPSE Fusion) Mapper
#
# This program is an open-source visual utility tool for the SFusion/SYNAPSE
# ecosystem. It is designed to create mapping configurations (as .db files)
# by associating traffic data sources (sensors, cameras, feeds) with a
# network topology map (e.g., SUMO .net.xml).
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
#    Map Controller (Controller). Handles the logic for the MapView,
#    such as drawing the map, handling zoom/pan logic (if complex),
#    and processing user clicks on map elements.

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

# Import the View
from ui.map.map_view import MapView

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import ElementType

# Import other controllers (for type hinting)
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.controllers.sources_controller import SourcesController


class MapController(QObject):
    """
    Map Controller (Controller).
    Manages the state and logic for the MapView component.
    """
    def __init__(self, view: MapView, app_state: AppState, parent=None):
        """
        Controller constructor.
        
        Args:
            view (MapView): The map view instance.
            app_state (AppState): The application state model.
        """
        super().__init__(parent)
        
        # Store references to the View and Model
        self.view = view
        self.app_state = app_state
        
        # Reference to other controllers (set by MainController)
        self.sources_controller: 'SourcesController' = None
        
        # Internal state for this controller
        self.selection_mode_active = False
        self.source_id_to_associate: Optional[str] = None
        self.original_cursor = self.view.cursor()
        
        print("MapController: Initializing...")

        self._connect_signals()

    def set_sources_controller(self, controller: 'SourcesController'):
        """
        Sets the reference to the SourcesController for cross-communication.
        """
        self.sources_controller = controller

    def _connect_signals(self):
        """
        Connects signals from the MapView to slots in this controller.
        """
        # Listen to the click signals from the View
        self.view.nodeClicked.connect(self._on_node_clicked)
        self.view.edgeClicked.connect(self._on_edge_clicked)
        
        print("MapController: View signals connected.")

    # --- Public API (called by MainController or other Controllers) ---

    def translate_ui(self, translator):
        """
        Applies translations to the MapView.
        (The MapView has no text, so this is a placeholder).
        """
        # t = translator
        # (No text to translate in this view)
        pass

    def draw_map(self):
        """
        Clears the current map and draws a new one based on AppState.
        Called by MainController after a map is loaded.
        """
        print(f"MapController: Received request to draw map...")
        
        map_data = self.app_state.get_map_data()
        
        # 1. Clear the old map from the view
        self.view.clear_map()
        
        if not map_data:
            print("MapController: No map data in state. Map cleared.")
            return

        # 2. Draw the new map
        try:
            print(f"MapController: Drawing {len(map_data.nodes)} nodes...")
            for node in map_data.nodes:
                self.view.draw_node(node.id, node.x, node.y)
                
            print(f"MapController: Drawing {len(map_data.edges)} edges...")
            for edge in map_data.edges:
                self.view.draw_edge(edge.id, edge.shape)
                
            print("MapController: Map drawn successfully.")
            
            # 3. Fit the view to the newly drawn items
            self.view.fit_to_scene()
            
        except Exception as e:
            print(f"MapController: Error drawing map: {e}")
            # TODO: Report this error to the main status bar

    def enter_selection_mode(self, source_id: str):
        """
        Called by SourcesController when "Associate" is clicked.
        Puts the map in a state to capture the next click FOR a specific source.
        
        Args:
            source_id (str): The ID of the source to associate.
        """
        print(f"MapController: Entering selection mode for source ID: {source_id}...")
        self.selection_mode_active = True
        self.source_id_to_associate = source_id
        
        # Change cursor to crosshairs
        self.view.setCursor(Qt.CrossCursor)

    def _exit_selection_mode(self):
        """ Internal helper to restore normal state. """
        print("MapController: Exiting selection mode.")
        self.selection_mode_active = False
        self.source_id_to_associate = None
        # Restore original cursor
        self.view.setCursor(self.original_cursor)

    # --- SLOTS (responding to View signals) ---

    @Slot(str)
    def _on_node_clicked(self, node_id):
        """
        Slot for when a node is clicked in the MapView.
        """
        print(f"MapController: Node '{node_id}' clicked.")
        
        if not self.selection_mode_active or self.source_id_to_associate is None:
            print("MapController: Click ignored (not in selection mode).")
            return # Ignore clicks if not in selection mode

        print(f"MapController: Associating source {self.source_id_to_associate} with NODE {node_id}.")
        
        # 1. Update the Model (AppState)
        source = self.app_state.get_source(self.source_id_to_associate)
        if not source:
            print(f"Error: Could not find source {self.source_id_to_associate} in AppState.")
            self._exit_selection_mode()
            return

        source.set_local_association(node_id, ElementType.NODE)
        
        # 2. Tell the SourcesController to update its view
        if self.sources_controller:
            self.sources_controller.update_association_status(f"Node: {node_id}", self.source_id_to_associate)
            
        # 3. Exit selection mode
        self._exit_selection_mode()

    @Slot(str)
    def _on_edge_clicked(self, edge_id):
        """
        Slot for when an edge is clicked in the MapView.
        """
        print(f"MapController: Edge '{edge_id}' clicked.")
        
        if not self.selection_mode_active or self.source_id_to_associate is None:
            print("MapController: Click ignored (not in selection mode).")
            return

        print(f"MapController: Associating source {self.source_id_to_associate} with EDGE {edge_id}.")
        
        # 1. Update the Model (AppState)
        source = self.app_state.get_source(self.source_id_to_associate)
        if not source:
            print(f"Error: Could not find source {self.source_id_to_associate} in AppState.")
            self._exit_selection_mode()
            return
            
        source.set_local_association(edge_id, ElementType.EDGE)
        
        # 2. Tell the SourcesController to update its view
        if self.sources_controller:
            self.sources_controller.update_association_status(f"Edge: {edge_id}", self.source_id_to_associate)

        # 3. Exit selection mode
        self._exit_selection_mode()