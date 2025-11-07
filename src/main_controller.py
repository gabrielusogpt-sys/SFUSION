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

# File: src/main_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Main Controller (Controller). Connects the MainWindow (View) signals
#    to the application logic (Model). It handles toolbar actions and
#    coordinates the other controllers.

# --- SRP Refactor ---
# This class is now "clean". It no longer handles bootstrapping.
# Its sole responsibility is to handle toolbar actions by coordinating
# components that are *injected* into it by the AppBuilder.

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog
from typing import TYPE_CHECKING

# Import the View
from ui.main_window import MainWindow

# Import Model components
from src.domain.entities import DataSource

# Type hints for injected components
if TYPE_CHECKING:
    from src.controllers.map_controller import MapController
    from src.controllers.sources_controller import SourcesController
    from src.domain.app_state import AppState
    from src.utils.i18n import I18nManager
    from src.utils.config import ConfigManager
    from src.services.map_importer import MapImporter
    from src.services.data_importer import DataImporter
    from src.services.persistence import PersistenceService


class MainController(QObject):
    """
    Main Controller (Controller).
    Connects the MainWindow (View) signals to the application logic (Model).
    """
    def __init__(
        self, 
        view: MainWindow,
        app_state: 'AppState',
        config: 'ConfigManager',
        i18n_frontend: 'I18nManager',
        i18n_backend: 'I18nManager',
        map_controller: 'MapController',
        sources_controller: 'SourcesController',
        map_importer: 'MapImporter',
        data_importer: 'DataImporter',
        persistence_service: 'PersistenceService',
        parent=None
    ):
        """
        Controller constructor (Refactored for SRP).
        
        This controller is "clean" and receives all its dependencies
        (Dependency Injection) from the AppBuilder.
        """
        super().__init__(parent)
        
        print("MainController: Initializing...")

        # --- Store Injected Dependencies ---
        self.view = view
        self.app_state = app_state
        self.config = config
        self.i18n_frontend = i18n_frontend
        self.i18n_backend = i18n_backend
        self.map_controller = map_controller
        self.sources_controller = sources_controller
        self.map_importer = map_importer
        self.data_importer = data_importer
        self.persistence_service = persistence_service
        
        # --- Initialize Own Responsibilities ---
        self._setup_translations()
        self._connect_signals()
        
        print("MainController: Initialization complete. Application ready.")

    def _setup_translations(self):
        """
        Loads the i18n manager and applies translations to the "dumb" view.
        """
        t = self.i18n_frontend.t # Alias for easier access
        try:
            self.view.setWindowTitle(t("main_window.window_title"))
            
            # Toolbar
            self.view.main_toolbar.setWindowTitle(t("toolbar.main"))
            self.view.open_map_action.setText(t("toolbar.open_map"))
            self.view.open_map_action.setToolTip(t("toolbar.open_map_tooltip"))
            self.view.add_source_action.setText(t("toolbar.add_source"))
            self.view.add_source_action.setToolTip(t("toolbar.add_source_tooltip"))
            self.view.save_map_action.setText(t("toolbar.save_map"))
            self.view.save_map_action.setToolTip(t("toolbar.save_map_tooltip"))
            
            # Status Bar
            self.view.status_bar.showMessage(t("status_bar.ready"))
            
            # Let controllers translate their own components
            self.map_controller.translate_ui(t)
            self.sources_controller.translate_ui(t)

        except Exception as e:
            print(f"Error applying translations: {e}")
            self.view.status_bar.showMessage("Error: Could not load translations.")
        
    def _connect_signals(self):
        """
        Connects signals from the View (MainWindow) to slots in this controller.
        """
        self.view.open_map_action.triggered.connect(self._on_open_map)
        self.view.add_source_action.triggered.connect(self._on_add_source)
        self.view.save_map_action.triggered.connect(self._on_save_map)
        
        print("MainController: View signals connected to controller slots.")

    # --- SLOTS (Application Logic) ---
    # (These methods remain unchanged as they use the injected dependencies)

    @Slot()
    def _on_open_map(self):
        """ Slot for when the 'Open Map' action is triggered. """
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            self.i18n_frontend.t("dialog.open_map.title"),
            self.config.get("last_map_directory", "."),
            self.i18n_frontend.t("dialog.open_map.filter")
        )
        
        if not file_path:
            return # User canceled

        try:
            self.view.status_bar.showMessage(f"Loading map: {file_path}...")
            # 1. Call the Map Importer service
            map_data = self.map_importer.load_file(file_path)
            
            # 2. Update the Model (AppState)
            self.app_state.set_map_data(map_data, file_path)
            
            # 3. Tell MapController to update the View
            self.map_controller.draw_map()
            
            # 4. Tell SourcesController to update (clear) its View
            self.sources_controller.refresh_list()
            
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.map_loaded").format(path=file_path))
            
        except Exception as e:
            print(f"Error loading map: {e}")
            error_msg = self.i18n_backend.t("errors.map_importer.invalid_xml").format(error=e)
            self.view.status_bar.showMessage(error_msg)

    @Slot()
    def _on_add_source(self):
        """ Slot for when the 'Add Data Source' action is triggered. """
        
        folder_path = QFileDialog.getExistingDirectory(
            self.view,
            self.i18n_frontend.t("dialog.add_source.title")
        )
        
        if not folder_path:
            return # User canceled

        try:
            self.view.status_bar.showMessage(f"Analyzing folder: {folder_path}...")
            
            # 1. Call the Data Importer service
            analysis = self.data_importer.analyze_folder(folder_path)
            
            # 2. Create the new Model entity
            new_source = DataSource(
                path=folder_path,
                parser_id=analysis.get("file_type")
            )
            
            # 3. Update the Model (AppState)
            self.app_state.add_source(new_source)
            
            # 4. Tell SourcesController to update its View
            self.sources_controller.refresh_list()
            
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.source_added").format(path=folder_path))

        except Exception as e:
            print(f"Error analyzing folder: {e}")
            error_msg = self.i18n_backend.t("errors.data_importer.analysis_failed").format(error=e)
            self.view.status_bar.showMessage(error_msg)

    @Slot()
    def _on_save_map(self):
        """ Slot for when the 'Save Mapping' action is triggered. """
        
        map_path = self.app_state.get_map_file_path()
        if not map_path:
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.save_no_map_error"))
            return # Can't save without a map loaded
        
        save_path, _ = QFileDialog.getSaveFileName(
            self.view,
            self.i18n_frontend.t("dialog.save_map.title"),
            "mapping.db",
            self.i18n_frontend.t("dialog.save_map.filter")
        )

        if not save_path:
            return # User canceled

        try:
            self.view.status_bar.showMessage(f"Saving to {save_path}...")
            
            # 1. Get all data from the Model (AppState)
            all_sources = self.app_state.get_all_sources()
            
            # 2. Call the Persistence Service
            self.persistence_service.save_mapping(
                save_path=save_path,
                map_base_path=map_path,
                data_sources=all_sources
            )
            
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.save_success").format(path=save_path))
            
        except Exception as e:
            print(f"Error saving file: {e}")
            error_msg = self.i18n_backend.t("errors.persistence.save_failed").format(error=e)
            self.view.status_bar.showMessage(error_msg)