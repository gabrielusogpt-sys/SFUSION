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

# File: ui/sources/sources_panel.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Defines the SourcesPanel (QWidget), a composite widget for the
#    left side of the UI. It contains the list of data sources and the
#    details/editor panel for the selected source.

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QGroupBox,
    QFormLayout,
    QRadioButton,
    QPushButton,
    QLabel,
    QSplitter,
    QListWidgetItem
)

class SourcesPanel(QWidget):
    """
    The SourcesPanel (View) component.

    This class provides the UI for listing, adding, and editing the
    properties of data sources (e..g, setting them as Global/Local
    and associating them with map elements).
    
    It is a "dumb" component that emits signals (e.g., source_selected)
    and whose fields are populated by a Controller.
    """
    def __init__(self, parent=None):
        """
        SourcesPanel constructor.
        """
        super().__init__(parent)

        # Main layout for this widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Use full space

        # Create a vertical splitter to divide list and details
        self.splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.splitter)

        # Create the top part: the list of sources
        self.sources_list_widget = self._create_sources_list_widget()
        self.splitter.addWidget(self.sources_list_widget)

        # Create the bottom part: the details editor
        self.details_widget = self._create_details_widget()
        self.splitter.addWidget(self.details_widget)

        # Set initial sizes
        self.splitter.setStretchFactor(0, 2) # List (top) gets 2/3 of space
        self.splitter.setStretchFactor(1, 1) # Details (bottom) gets 1/3

    def _create_sources_list_widget(self):
        """
        Creates the top widget (QGroupBox) containing the QListWidget.
        """
        # Use a GroupBox for a nice title
        list_group = QGroupBox("Data Sources") # Placeholder text
        list_layout = QVBoxLayout(list_group)
        
        self.sources_list = QListWidget()
        # TODO: The controller will add items here
        
        list_layout.addWidget(self.sources_list)
        return list_group

    def _create_details_widget(self):
        """
        Creates the bottom widget (QGroupBox) containing the editor
        for the selected data source.
        """
        self.details_group = QGroupBox("Source Details") # Placeholder text
        details_layout = QFormLayout(self.details_group)

        # --- Widgets for the details editor ---
        
        # 1. Type selection (Global vs Local)
        self.radio_global = QRadioButton("Global") # Placeholder text
        self.radio_local = QRadioButton("Local") # Placeholder text
        
        type_layout = QVBoxLayout()
        type_layout.addWidget(self.radio_global)
        type_layout.addWidget(self.radio_local)
        
        details_layout.addRow("Type:", type_layout) # Placeholder text

        # 2. Association button
        self.associate_button = QPushButton("Associate with Map Element")
        details_layout.addRow(self.associate_button)

        # 3. Status label
        self.status_label = QLabel("Not associated.") # Placeholder text
        details_layout.addRow("Status:", self.status_label) # Placeholder text
        
        # The details panel should be disabled until a source is selected
        self.details_group.setEnabled(False)
        
        return self.details_group

    # --- Public Methods (for the Controller) ---

    def add_source_to_list(self, name, id):
        """
        Adds a new item to the sources list.
        Called by the controller.
        """
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, id) # Store a unique ID in the item
        self.sources_list.addItem(item)
        
    def clear_sources_list(self):
        """ Clears all items from the list. """
        self.sources_list.clear()

    def set_details_enabled(self, enabled):
        """
        Enables or disables the entire details panel.
        """
        self.details_group.setEnabled(enabled)

# --- This block allows you to run this file directly for testing ---
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    panel = SourcesPanel()
    panel.setWindowTitle("SourcesPanel Test")
    panel.resize(400, 600)
    
    # Add some dummy data for testing
    panel.add_source_to_list("/data/cameras/", "id_cam_1")
    panel.add_source_to_list("/data/waze/", "id_waze_1")
    panel.add_source_to_list("/data/loops/", "id_loop_1")
    
    panel.show()
    sys.exit(app.exec())