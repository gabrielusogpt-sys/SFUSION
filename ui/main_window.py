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

# File: ui/main_window.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Defines the main application window (QMainWindow), which acts as the
#    "shell" for all other UI components (toolbar, map view, source panel).

import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QStatusBar,
    QSplitter,
    QWidget
)

# Import the actual components
from ui.map.map_view import MapView
from ui.sources.sources_panel import SourcesPanel

class MainWindow(QMainWindow):
    """
    The main application window (View).

    This class is responsible only for the layout and visual presentation
    of the main components. It is a "dumb" component (View).
    It emits signals that the MainController will connect to.
    """
    def __init__(self, parent=None):
        """
        Main window constructor.
        """
        super().__init__(parent)
        
        # This function will contain all UI setup code
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the main UI components and layout.
        """
        # Set window properties (title will be set by controller via i18n)
        self.setWindowTitle("SFusion Mapper")
        self.resize(1200, 800) # Default window size

        # Create components
        self._create_actions()
        self._create_toolbars()
        self._create_central_widget()
        self._create_status_bar()

    def _create_actions(self):
        """
        Creates all the QAction objects for the application.
        These actions are used by menus and toolbars.
        """
        # Placeholder icons (paths will be managed by assets module later)
        # TODO: Replace with QResource loading from assets/
        icon_path = "assets/icons/"

        # Action for opening a map
        self.open_map_action = QAction(
            QIcon(f"{icon_path}open.png"), # Placeholder icon
            "Open Map", # Placeholder text (will be set by controller)
            self
        )
        self.open_map_action.setToolTip("Open a SUMO .net.xml map file")

        # Action for adding a data source folder
        self.add_source_action = QAction(
            QIcon(f"{icon_path}add_folder.png"), # Placeholder icon
            "Add Data Source", # Placeholder text
            self
        )
        self.add_source_action.setToolTip("Add a folder containing data files")

        # Action for saving the mapping configuration
        self.save_map_action = QAction(
            QIcon(f"{icon_path}save.png"), # Placeholder icon
            "Save Mapping", # Placeholder text
            self
        )
        self.save_map_action.setToolTip("Save the mapping configuration to a .db file")

    def _create_toolbars(self):
        """
        Creates and configures the main application toolbar.
        """
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.main_toolbar)

        # Add actions to the toolbar
        self.main_toolbar.addAction(self.open_map_action)
        self.main_toolbar.addAction(self.add_source_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.save_map_action)

    def _create_central_widget(self):
        """
        Creates the main layout (a splitter) to hold the
        sources panel and the map view.
        """
        # Main layout is a horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)

        # --- Instantiate the real components ---
        
        # Left Panel (Sources List and Details)
        self.sources_panel = SourcesPanel()

        # Right Panel (Map View)
        self.map_view = MapView()

        # Add panels to the splitter
        self.main_splitter.addWidget(self.sources_panel)
        self.main_splitter.addWidget(self.map_view)

        # Set initial sizes (Map panel is 3x wider than sources panel)
        self.main_splitter.setStretchFactor(0, 1) # Left panel (sources)
        self.main_splitter.setStretchFactor(1, 3) # Right panel (map)
        
    def _create_status_bar(self):
        """
        Creates the status bar at the bottom of the window.
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.") # Placeholder text

# --- This block allows you to run this file directly for testing ---
# (Useful to see if the layout looks correct)
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())