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

# File: ui/main_window.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Main Window (View). The main "shell" of the application.
#    It is a "dumb" component that just holds other widgets.

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QStatusBar, 
    QToolBar, 
    QHBoxLayout,
    QVBoxLayout # FIX: Import for the map container
)

# Import sub-widgets
from ui.map.map_view import MapView
from ui.sources.sources_panel import SourcesPanel

# --- FIX (Req 3): Import the new InfoPanel ---
from ui.map.info_panel import InfoPanel
# --- END FIX ---

class MainWindow(QMainWindow):
    """
    Main Window (View)
    
    The main "shell" of the application. It holds the toolbar,
    status bar, and the central widget (which contains the map
    and the sources panel).
    """
    def __init__(self, parent=None):
        """
        Constructor.
        """
        super().__init__(parent)
        
        # --- 1. Create Actions ---
        # (These will be configured by the controller)
        self.open_map_action = QAction("Open Map")
        self.add_source_action = QAction("Add Source")
        self.save_map_action = QAction("Save Map")
        
        # --- 2. Create UI Components ---
        self.main_toolbar = QToolBar("Main")
        self.status_bar = QStatusBar()
        
        # (Sub-widgets are created in _setup_ui)
        self.map_view = None
        self.sources_panel = None
        
        # --- FIX (Req 3): Add placeholder for info panel ---
        self.info_panel = None
        self.map_container = None
        # --- END FIX ---
        
        # --- 3. Setup Layout ---
        self._setup_ui()

    def _setup_ui(self):
        """
        Initializes and lays out the sub-widgets.
        """
        
        # --- 1. Configure Shell ---
        self.setWindowTitle("SFusion Mapper")
        self.setStatusBar(self.status_bar)
        
        # --- 2. Configure Toolbar ---
        self.main_toolbar.addAction(self.open_map_action)
        self.main_toolbar.addAction(self.add_source_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.save_map_action)
        self.addToolBar(self.main_toolbar)
        
        # --- 3. Create Main Widgets ---
        self.map_view = MapView()
        self.sources_panel = SourcesPanel()

        # --- 4. Setup Central Widget ---
        
        # --- FIX (Req 3): Create Map Container ---
        # This widget will hold the map AND the floating info panel
        self.map_container = QWidget()
        
        # Create the info panel as a child of the container
        self.info_panel = InfoPanel(self.map_container)
        # Position it in the top-left corner
        self.info_panel.setFixedSize(300, 150)
        self.info_panel.move(10, 10)
        self.info_panel.raise_() # Ensure it's on top
        
        # Create a layout for the container
        container_layout = QVBoxLayout(self.map_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        # Add the map view to fill the container
        container_layout.addWidget(self.map_view)
        # --- END FIX ---

        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        
        # Add the map container (which holds map + panel)
        central_layout.addWidget(self.map_container, 1) # Give it stretch factor 1
        # Add the sources panel
        central_layout.addWidget(self.sources_panel, 0) # No stretch
        
        self.setCentralWidget(central_widget)
        
        # --- 5. Set Initial State ---
        self.status_bar.showMessage("Ready.")
        self.resize(1200, 800)