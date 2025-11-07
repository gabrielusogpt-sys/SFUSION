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

# File: ui/map/info_panel.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Info Panel (View). A "dumb" widget to display details for a
#    selected map node or edge and allow editing its "real name".

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy
)

class InfoPanel(QGroupBox):
    """
    View component for the Node/Edge information panel.
    It is a "dumb" widget that emits signals when interacted with.
    """
    
    # Signal emitted when the save button is clicked.
    # It passes the (internal_id, new_real_name)
    saveClicked = Signal(str, str)
    
    # Signal emitted when the close button is clicked.
    closeClicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Constructor.
        """
        # Set the title of the GroupBox itself (often hidden by custom title bar)
        super().__init__("Element Details", parent)
        
        self._current_id: str | None = None
        
        # --- Create Widgets ---
        self.sumo_id_label = QLabel("N/A")
        self.sumo_id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.real_name_input = QLineEdit()
        self.real_name_input.setPlaceholderText("e.g., Main Street")

        self.save_button = QPushButton("Save")
        self.close_button = QPushButton("X") # Close button
        self.close_button.setFixedSize(24, 24)

        # --- Layouts ---
        
        # Title bar (Title + Close button)
        title_layout = QHBoxLayout()
        # FIX: Store title_label as self.title_label to be able to change it
        self.title_label = QLabel("Element Details") 
        title_layout.addWidget(self.title_label)
        # --- END FIX ---
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(self.close_button)
        
        # Form Layout
        form_layout = QFormLayout()
        form_layout.addRow("SUMO ID:", self.sumo_id_label)
        form_layout.addRow("Real Name:", self.real_name_input)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.save_button, 0, Qt.AlignRight)
        
        self.setLayout(main_layout)
        
        # --- Connections ---
        self.save_button.clicked.connect(self._on_save)
        self.close_button.clicked.connect(self.closeClicked)
        
        # Start hidden
        self.setVisible(False)

    def _on_save(self):
        """ Internal slot to emit the saveClicked signal with data. """
        if self._current_id:
            self.saveClicked.emit(self._current_id, self.real_name_input.text())

    # --- Public API (Called by Controller) ---

    def show_for_item(self, internal_id: str, real_name: str | None, item_type: str):
        """
        Populates the panel with data and makes it visible.
        
        Args:
            internal_id (str): The SUMO ID (e.g., "J1", "edge1").
            real_name (str | None): The current user-defined name.
            item_type (str): "Node" or "Edge", to update the title.
        """
        self._current_id = internal_id
        
        title_text = f"{item_type} Details"
        
        # --- FIX: Set title in both places correctly ---
        self.setTitle(title_text) # Set GroupBox title (in case it's visible)
        self.title_label.setText(title_text) # Set Label title
        # --- END FIX ---
        
        self.sumo_id_label.setText(internal_id)
        self.real_name_input.setText(real_name or "")
        
        self.setVisible(True)

    def hide_panel(self):
        """ Hides the panel. """
        self._current_id = None
        self.setVisible(False)