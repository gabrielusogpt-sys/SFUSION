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

# File: src/controllers/sources_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Sources Panel specialist (Controller). Connects the SourcesPanel (View)
#    signals to the application logic (Model).

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QListWidgetItem

from ui.sources.sources_panel import SourcesPanel
from src.domain.app_state import AppState
from src.domain.entities import AssociationType

# Need a type hint for the MapController, but don't import it
# to avoid a circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.controllers.map_controller import MapController


class SourcesController(QObject):
    """
    Controller for the Data Sources Panel.
    """
    def __init__(self, view: SourcesPanel, app_state: AppState, parent=None):
        """
        Controller constructor.
        
        Args:
            view (SourcesPanel): The view instance for the sources panel.
            app_state (AppState): The shared application state (Model).
        """
        super().__init__(parent)
        
        self.view = view
        self.app_state = app_state
        self.map_controller: 'MapController' = None # Set by MainController
        
        self._translator = None # Set by translate_ui
        
        self._connect_signals()
        
        # Disable details panel by default
        # --- FIX: Reverted attribute name to 'details_group' ---
        self.view.details_group.setEnabled(False)
        # --- END FIX ---

    def set_map_controller(self, map_controller: 'MapController'):
        """
        Sets the reference to the MapController for cross-communication.
        """
        self.map_controller = map_controller
        
    def translate_ui(self, translator):
        """
        Applies translations to the view components.
        
        Args:
            translator (callable): The i18n_frontend.t function.
        """
        self._translator = translator # Save for later status updates
        try:
            # --- FIX: Corrected translation keys (attributes are correct) ---
            self.view.list_group.setTitle(translator("sources_panel.group_title.list"))
            self.view.details_group.setTitle(translator("sources_panel.group_title.details"))
            
            self.view.id_label.setText(translator("sources_panel.label.id"))
            self.view.path_label.setText(translator("sources_panel.label.path"))
            self.view.type_label.setText(translator("sources_panel.label.type"))
            
            self.view.radio_global.setText(translator("sources_panel.radio.global"))
            self.view.radio_local.setText(translator("sources_panel.radio.local"))
            self.view.associate_button.setText(translator("sources_panel.button.associate"))
            
            self.view.status_label.setText(translator("sources_panel.label.status"))
            
            # Set default status text
            self.view.status_text_label.setText(
                translator("sources_panel.status.unassociated")
            )
            # --- END FIX ---
            
        except Exception as e:
            print(f"Error applying translations in SourcesController: {e}")

    def _connect_signals(self):
        """ Connects view signals to controller slots. """
        
        # When user clicks an item in the list
        self.view.sources_list.currentItemChanged.connect(self._on_source_selected)
        
        # When user changes association type
        self.view.radio_global.toggled.connect(self._on_type_changed)
        self.view.radio_local.toggled.connect(self._on_type_changed)
        
        # When user clicks the "Associate" button
        self.view.associate_button.clicked.connect(self._on_associate_clicked)

    def get_selected_source_id(self) -> str | None:
        """
        Gets the ID of the currently selected data source.
        """
        current_item = self.view.sources_list.currentItem()
        if current_item:
            return current_item.data(1) # Get data from custom role
        return None

    def refresh_list(self):
        """
        Reloads the list of data sources from the AppState (Model).
        """
        self.view.sources_list.clear()
        
        all_sources = self.app_state.get_all_sources()
        
        for source in all_sources:
            # Use path as the display text
            item = QListWidgetItem(source.path)
            # Store the unique ID in a custom role for retrieval
            item.setData(1, source.id) 
            self.view.sources_list.addItem(item)
            
        # Disable details panel if list is empty
        has_items = len(all_sources) > 0
        if not has_items:
            # --- FIX: Reverted attribute name to 'details_group' ---
            self.view.details_group.setEnabled(False)
            # --- END FIX ---

    def refresh_details(self, source_id: str | None = None):
        """
        Updates the details panel based on the selected source.
        If source_id is None, uses the currently selected list item.
        """
        if source_id is None:
            source_id = self.get_selected_source_id()

        # --- FIX: Reverted attribute name to 'details_group' ---
        if not source_id:
            self.view.details_group.setEnabled(False)
            return

        source = self.app_state.get_source_by_id(source_id)
        if not source:
            self.view.details_group.setEnabled(False)
            return
            
        # We have a valid source, enable and populate the panel
        self.view.details_group.setEnabled(True)
        # --- END FIX ---
        
        # Block signals while we set values to avoid triggering slots
        self.view.radio_global.blockSignals(True)
        self.view.radio_local.blockSignals(True)
        
        self.view.id_text_label.setText(source.id)
        self.view.path_text_label.setText(source.path)
        
        if source.association_type == AssociationType.GLOBAL:
            self.view.radio_global.setChecked(True)
            self._update_status_text(source)
            self.view.associate_button.setEnabled(False)
            
        elif source.association_type == AssociationType.LOCAL:
            self.view.radio_local.setChecked(True)
            self._update_status_text(source)
            self.view.associate_button.setEnabled(True)
            
        else: # Unassociated
            self.view.radio_local.setChecked(True) # Default to local
            self._update_status_text(source)
            self.view.associate_button.setEnabled(True)

        # Unblock signals
        self.view.radio_global.blockSignals(False)
        self.view.radio_local.blockSignals(False)

    def _update_status_text(self, source):
        """
        Updates the status label based on the source's state.
        """
        if not self._translator:
            return # Not ready yet
            
        t = self._translator
        
        if source.association_type == AssociationType.GLOBAL:
            # --- FIX: Corrected translation key ---
            self.view.status_text_label.setText(
                t("sources_panel.status.associated_global")
            )
        elif source.association_type == AssociationType.LOCAL and source.associated_node_id:
            # --- FIX: Corrected translation key ---
            self.view.status_text_label.setText(
                t("sources_panel.status.associated_node").format(node_id=source.associated_node_id)
            )
        else:
            # --- FIX: Corrected translation key ---
            self.view.status_text_label.setText(
                t("sources_panel.status.unassociated")
            )

    def notify_node_selection_mode(self, source_id: str, is_active: bool):
        """
        Called by MapController to update status when entering/exiting
        node selection mode.
        """
        if not self._translator or self.get_selected_source_id() != source_id:
            return
            
        t = self._translator
        
        if is_active:
            # --- FIX: Corrected translation key ---
            self.view.status_text_label.setText(
                t("sources_panel.status.selecting_node")
            )
        else:
            # Mode was canceled, restore status
            source = self.app_state.get_source_by_id(source_id)
            self._update_status_text(source)

    # --- SLOTS ---

    @Slot(QListWidgetItem)
    def _on_source_selected(self, current_item: QListWidgetItem):
        """
        Slot triggered when the user selects a new source from the list.
        """
        # --- FIX: Reverted attribute name to 'details_group' ---
        if not current_item:
            self.view.details_group.setEnabled(False)
            return
        # --- END FIX ---
            
        source_id = current_item.data(1) # Get ID from custom role
        self.refresh_details(source_id)
        
        # Tell map controller to cancel node selection if it was active
        if self.map_controller:
            self.map_controller.cancel_node_selection()

    @Slot(bool)
    def _on_type_changed(self, checked: bool):
        """
        Slot triggered when user clicks a radio button (Global/Local).
        """
        # We only care about the button that was *checked*
        if not checked:
            return

        source_id = self.get_selected_source_id()
        if not source_id:
            return
            
        source = self.app_state.get_source_by_id(source_id)

        if self.view.radio_global.isChecked():
            # 1. Update Model
            source.association_type = AssociationType.GLOBAL
            source.associated_node_id = None
            
            # 2. Update View (Details Panel)
            self.view.associate_button.setEnabled(False)
            self._update_status_text(source)
            
            # 3. Update View (Map)
            if self.map_controller:
                self.map_controller.cancel_node_selection()
                self.map_controller.clear_selection_highlight()
            
        elif self.view.radio_local.isChecked():
            # 1. Update Model
            source.association_type = AssociationType.LOCAL
            # Note: We don't clear the associated_node_id here.
            # If one was previously set, we keep it.
            
            # 2. Update View (Details Panel)
            self.view.associate_button.setEnabled(True)
            self._update_status_text(source)
            
            # 3. Update View (Map)
            if self.map_controller:
                self.map_controller.highlight_node(source.associated_node_id)
                
    @Slot()
    def _on_associate_clicked(self):
        """
        Slot triggered when the user clicks the "Associate with Map..."
        button.
        """
        source_id = self.get_selected_source_id()
        if not source_id or not self.map_controller:
            return

        # Tell the MapController to enter node selection mode
        self.map_controller.start_node_selection(source_id)