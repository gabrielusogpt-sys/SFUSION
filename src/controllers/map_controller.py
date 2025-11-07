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
#    to the application logic (Model). Handles interaction logic and state.
#    (Refactored for SRP: Rendering logic is in MapRenderer).

from PySide6.QtCore import QObject, Slot, Qt, QPoint
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

# Import the View
from ui.map.map_view import MapView

# Import Model components
from src.domain.app_state import AppState

# Need type hints, but don't import to avoid circular dependencies
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.controllers.sources_controller import SourcesController
    from src.core.map_renderer import MapRenderer # SRP Refactor
    from src.controllers.info_controller import InfoController # FIX (Req 3)


class MapController(QObject):
    """
    Controller for the Map View. (The "Brain")
    Handles interaction logic and state management.
    Delegates all drawing to the MapRenderer.
    """
    
    def __init__(
        self, 
        view: MapView, 
        app_state: AppState, 
        renderer: 'MapRenderer', # SRP Refactor: Injected dependency
        parent=None
    ):
        """
        Controller constructor.
        
        Args:
            view (MapView): The view instance for the map.
            app_state (AppState): The shared application state (Model).
            renderer (MapRenderer): The "Painter" responsible for drawing.
        """
        super().__init__(parent)
        
        self.view = view
        self.app_state = app_state
        self.renderer = renderer # SRP Refactor: Store the renderer
        
        # --- FIX (Req 3): Add placeholder for InfoController ---
        self.info_controller: 'InfoController' = None
        # --- END FIX ---
        
        self.sources_controller: 'SourcesController' = None # Set by MainController
        
        self._translator = None
        
        # State for node selection
        self._is_selecting_node = False
        self._selection_source_id = None
        
        self._setup_context_menu()
        self._connect_signals()
        print("MapController: Initialized.")

    def set_sources_controller(self, sources_controller: 'SourcesController'):
        """
        Sets the reference to the SourcesController for cross-communication.
        """
        self.sources_controller = sources_controller

    # --- FIX (Req 3): Add setter for InfoController ---
    def set_info_controller(self, info_controller: 'InfoController'):
        """
        Sets the reference to the InfoController.
        Called by AppBuilder.
        """
        self.info_controller = info_controller
    # --- END FIX ---

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
        
        # --- FIX (Req 3): Connect the new edge click signal ---
        self.view.edgeClicked.connect(self._on_edge_clicked)
        # --- END FIX ---
        
        # Custom signal from MapView (View)
        self.view.emptySpaceClicked.connect(self._on_empty_space_clicked)
        # Custom signal from MapView (View)
        self.view.customContextMenuRequested.connect(self._on_context_menu)
        
    # --- Public API (Called by MainController) ---

    def draw_map(self):
        """
        Delegates the draw call to the MapRenderer.
        """
        print("MapController: Delegating 'draw_map' to MapRenderer.")
        self.renderer.draw_map()

    def highlight_node(self, node_id: str | None):
        """
        Delegates the highlight call to the MapRenderer.
        """
        self.renderer.highlight_node(node_id)

    def clear_selection_highlight(self):
        """
        Delegates the clear highlight call to the MapRenderer.
        """
        self.renderer.clear_selection_highlight()

    # --- State Management Logic ---

    def start_node_selection(self, source_id: str):
        """
        Enters "node selection" mode. The next node click will be
        captured to associate with the given source_id.
        """
        self._is_selecting_node = True
        self._selection_source_id = source_id
        
        # 1. Update View (Cursor)
        self.view.setCursor(Qt.CrossCursor)
        
        # --- FIX (Req 3): Hide info panel when selecting ---
        if self.info_controller:
            self.info_controller.hide_panel()
        # --- END FIX ---
        
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

    # --- SLOTS (Interaction Logic) ---

    @Slot(str)
    def _on_node_clicked(self, node_id: str):
        """
        Slot triggered by the View when a node item is clicked.
        This is pure interaction logic.
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

            # 2. Delegate drawing to Renderer
            self.renderer.highlight_node(node_id)
            
            # 3. Exit selection mode (State logic)
            self.cancel_node_selection()
            
            # 4. Notify SourcesController (Coordination logic)
            if self.sources_controller:
                self.sources_controller.refresh_details(source_id)
                
        else:
            # --- We are in "normal" mode ---
            
            # 1. Delegate drawing to Renderer
            self.renderer.highlight_node(node_id)
            
            # --- FIX (Req 3): Show Info Box ---
            if self.info_controller:
                self.info_controller.show_for_node(node_id)
            # --- END FIX ---

    # --- FIX (Req 3): Add the new slot for edge clicks ---
    @Slot(str)
    def _on_edge_clicked(self, edge_id: str):
        """
        Slot triggered by the View when an edge item is clicked.
        """
        print(f"MapController: Edge '{edge_id}' clicked.")
        
        # In normal mode (not selecting a node)
        if not self._is_selecting_node:
            
            # TODO: Implement edge highlighting in MapRenderer
            # self.renderer.highlight_edge(edge_id)
            
            # --- FIX (Req 3): Show Info Box ---
            if self.info_controller:
                self.info_controller.show_for_edge(edge_id)
            # --- END FIX ---
    # --- END FIX ---

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
        # 1. Delegate drawing to Renderer
        self.renderer.clear_selection_highlight()
        
        # --- FIX (Req 3): Hide info panel ---
        if self.info_controller:
            self.info_controller.hide_panel()
        # --- END FIX ---
        
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