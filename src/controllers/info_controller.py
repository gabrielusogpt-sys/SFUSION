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

# File: src/controllers/info_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Info Panel specialist (Controller). Connects the InfoPanel (View)
#    signals to the application logic (Model).

from PySide6.QtCore import QObject, Slot

# Import the View this controller manages
from ui.map.info_panel import InfoPanel

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import MapNode, MapEdge

class InfoController(QObject):
    """
    Controller for the Map Info Panel. (Req 3)
    Handles showing/hiding the panel and saving "real name" data.
    """
    def __init__(self, view: InfoPanel, app_state: AppState, parent=None):
        """
        Controller constructor.
        
        Args:
            view (InfoPanel): The view instance for the info panel.
            app_state (AppState): The shared application state (Model).
        """
        super().__init__(parent)
        
        self.view = view
        self.app_state = app_state
        self._current_item_type: str | None = None # "node" or "edge"
        
        self._connect_signals()
        print("InfoController: Initialized.")

    def _connect_signals(self):
        """ Connects view signals to controller slots. """
        self.view.saveClicked.connect(self._on_save)
        self.view.closeClicked.connect(self._on_close)
        
    # --- Public API (Called by MapController) ---

    def show_for_node(self, node_id: str):
        """
        Commands the InfoPanel to show data for a specific node.
        """
        node = self.app_state.get_node_by_id(node_id)
        if node:
            self._current_item_type = "node"
            self.view.show_for_item(node.id, node.real_name, "Node")
        else:
            print(f"InfoController: Error: Node {node_id} not found in AppState.")

    def show_for_edge(self, edge_id: str):
        """
        Commands the InfoPanel to show data for a specific edge.
        """
        # NOTE: self.app_state.get_edge_by_id does not exist yet.
        # We must add it to src/domain/app_state.py next.
        edge = self.app_state.get_edge_by_id(edge_id)
        
        if edge:
            self._current_item_type = "edge"
            self.view.show_for_item(edge.id, edge.real_name, "Edge")
        else:
            print(f"InfoController: Error: Edge {edge_id} not found in AppState.")
            
    def hide_panel(self):
        """ Commands the InfoPanel to hide. """
        self.view.hide_panel()
        self._current_item_type = None

    # --- Slots (Called by View) ---

    @Slot(str, str)
    def _on_save(self, item_id: str, new_real_name: str):
        """
        Slot triggered when the view's 'Save' button is clicked.
        Updates the Model (AppState).
        """
        print(f"InfoController: Saving '{new_real_name}' for {self._current_item_type} {item_id}")
        
        # Ensure the name is saved as None if the string is empty
        saved_name = new_real_name if new_real_name.strip() else None
        
        item = None
        if self._current_item_type == "node":
            item = self.app_state.get_node_by_id(item_id)
        elif self._current_item_type == "edge":
            item = self.app_state.get_edge_by_id(item_id)
        
        if item:
            item.real_name = saved_name
            print(f"InfoController: Model (AppState) updated for {item_id}.")
        else:
            print(f"InfoController: Error: Could not find item {item_id} to save.")
        
        self.hide_panel()

    @Slot()
    def _on_close(self):
        """
        Slot triggered when the view's 'Close' button is clicked.
        """
        self.hide_panel()