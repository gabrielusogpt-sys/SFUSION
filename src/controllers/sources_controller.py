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

# File: src/controllers/sources_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Sources Controller (Controller). Handles the logic for the SourcesPanel,
#    such as adding new sources to the list, editing source properties
#    (Global/Local), and managing the association process.

from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtWidgets import QListWidgetItem

# Import the View
from ui.sources.sources_panel import SourcesPanel

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import SourceType, ElementType, DataSource

# Import other controllers (for type hinting)
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.controllers.map_controller import MapController


class SourcesController(QObject):
    """
    Sources Controller (Controller).
    Manages the state and logic for the SourcesPanel component.
    """
    def __init__(self, view: SourcesPanel, app_state: AppState, parent=None):
        """
        Controller constructor.
        
        Args:
            view (SourcesPanel): The sources panel view instance.
            app_state (AppState): The application state model.
        """
        super().__init__(parent)
        
        # Store references to the View and Model
        self.view = view
        self.app_state = app_state
        
        # Reference to other controllers (set by MainController)
        self.map_controller: 'MapController' = None
        self.translator = None # Placeholder for i18n function
        
        print("SourcesController: Initializing...")

        self._connect_signals()

    def set_map_controller(self, controller: 'MapController'):
        """
        Sets the reference to the MapController for cross-communication.
        """
        self.map_controller = controller

    def _connect_signals(self):
        """
        Connects signals from the SourcesPanel to slots in this controller.
        """
        self.view.sources_list.currentItemChanged.connect(self._on_source_selected)
        self.view.radio_local.toggled.connect(self._on_type_changed)
        self.view.associate_button.clicked.connect(self._on_associate_clicked)
        
        print("SourcesController: View signals connected.")

    def _get_current_source(self) -> Optional[DataSource]:
        """ Helper method to get the DataSource for the selected list item. """
        current_item = self.view.sources_list.currentItem()
        if not current_item:
            return None
        
        source_id = current_item.data(Qt.UserRole)
        return self.app_state.get_source(source_id)

    # --- Public API (called by MainController or other Controllers) ---

    def translate_ui(self, translator):
        """
        Applies translations to the SourcesPanel.
        Called by MainController.
        """
        self.translator = translator # Store for later use
        t = translator
        
        self.view.sources_list_widget.setTitle(t("sources_panel.list_title"))
        self.view.details_group.setTitle(t("sources_panel.details_title"))
        
        # Find the label for the radio buttons
        type_label = self.view.details_group.layout().labelForField(self.view.radio_local.parent())
        if type_label:
            type_label.setText(t("sources_panel.type_label"))
            
        self.view.radio_global.setText(t("sources_panel.type_global"))
        self.view.radio_local.setText(t("sources_panel.type_local"))
        self.view.associate_button.setText(t("sources_panel.associate_button"))

        # Find the label for the status
        status_label = self.view.details_group.layout().labelForField(self.view.status_label)
        if status_label:
            status_label.setText(t("sources_panel.status_label"))
            
        self.view.status_label.setText(t("sources_panel.status_not_associated"))

    def refresh_list(self):
        """
        Reloads the list of sources from the AppState.
        Called by MainController when the data changes (e.g., map load, source add).
        """
        print("SourcesController: Refreshing source list...")
        self.view.clear_sources_list()
        self.view.set_details_enabled(False) # Disable details panel
        
        all_sources = self.app_state.get_all_sources()
        for source in all_sources:
            # Use the path as the display name
            self.view.add_source_to_list(source.path, source.id)

    def update_association_status(self, association_text: str, source_id: str):
        """
        Called by MapController after an association is made.
        This updates the status label for the *currently selected* item.
        """
        current_source = self._get_current_source()
        if current_source and current_source.id == source_id:
            self.view.status_label.setText(association_text)

    # --- SLOTS (responding to View signals) ---

    @Slot(QListWidgetItem, QListWidgetItem)
    def _on_source_selected(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        """
        Slot for when the user selects an item in the QListWidget.
        """
        if current_item is None:
            print("SourcesController: Source selection cleared.")
            self.view.set_details_enabled(False)
            return

        source = self._get_current_source()
        if not source:
            return # Should not happen if item exists

        print(f"SourcesController: Source '{source.path}' selected.")

        # Enable the details panel
        self.view.set_details_enabled(True)
        
        # Update the view fields to match the data from AppState
        self.view.radio_local.setChecked(source.is_local)
        self.view.radio_global.setChecked(not source.is_local)
        
        if source.is_local and source.association:
            assoc_type = "Node" if source.association.element_type == ElementType.NODE else "Edge"
            assoc_id = source.association.element_id
            self.view.status_label.setText(f"{assoc_type}: {assoc_id}")
        else:
            self.view.status_label.setText(self.translator("sources_panel.status_not_associated"))

    @Slot(bool)
    def _on_type_changed(self, is_local_selected):
        """
        Slot for when the 'Local' radio button is toggled.
        Updates the AppState.
        """
        source = self._get_current_source()
        if not source:
            return # No item selected, do nothing

        if is_local_selected:
            print(f"SourcesController: Setting source {source.id} to LOCAL.")
            source.source_type = SourceType.LOCAL
            self.view.associate_button.setEnabled(True)
        else:
            print(f"SourcesController: Setting source {source.id} to GLOBAL.")
            source.set_global() # This clears the association
            self.view.associate_button.setEnabled(False)
            # Update the view status label immediately
            self.view.status_label.setText(self.translator("sources_panel.status_not_associated"))
        
    @Slot()
    def _on_associate_clicked(self):
        """
        Slot for when the 'Associate with Map Element' button is clicked.
        """
        source = self._get_current_source()
        if not source or not self.map_controller:
            return
            
        print(f"SourcesController: 'Associate' clicked for source {source.id}.")
        
        # 1. Tell the MapController to enter "selection mode"
        self.map_controller.enter_selection_mode(source.id)
        
        # 2. Update the view status
        # TODO: Add this key to locale files
        status_text = self.translator("sources_panel.status_selecting")
        self.view.status_label.setText(status_text)
        
        # 3. Tell MainController to update the main status bar
        # self.main_view.status_bar.showMessage(status_text)