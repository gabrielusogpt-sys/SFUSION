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

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog

# Import the View
from ui.main_window import MainWindow

# Import other Controllers
from src.controllers.map_controller import MapController
from src.controllers.sources_controller import SourcesController

# Import Model components
from src.domain.app_state import AppState
from src.domain.entities import DataSource
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
    def __init__(self, view: MainWindow, parent=None):
        """
        Controller constructor.
        
        Args:
            view (MainWindow): The main window view instance.
        """
        super().__init__(parent)
        
        # Store reference to the View
        self.view = view
        
        print("MainController: Initializing...")

        # --- Initialize Model and Services ---
        
        # 1. Config
        self.config = ConfigManager("config/settings.json")
        self.config.load_config()
        
        # 2. i18n
        default_lang = self.config.get("default_language", "en")
        self.i18n_frontend = I18nManager("locale")
        self.i18n_backend = I18nManager("locale_backend")
        try:
            self.i18n_frontend.load_language(default_lang)
            self.i18n_backend.load_language(default_lang)
            print(f"MainController: Language '{default_lang}' loaded.")
        except Exception as e:
            print(f"CRITICAL: Failed to load language files: {e}")
            # The app will run, but with KEY_NOT_FOUND errors

        # 3. Application State (Single Source of Truth)
        self.app_state = AppState()

        # 4. Services (Workers)
        self.map_importer = MapImporter()
        self.data_importer = DataImporter()
        self.persistence_service = PersistenceService()

        # --- Initialize Sub-Controllers ---
        # Pass the Model (AppState) and other components to the specialists
        
        self.map_controller = MapController(
            view=self.view.map_view, 
            app_state=self.app_state
        )
        
        self.sources_controller = SourcesController(
            view=self.view.sources_panel, 
            app_state=self.app_state
        )

        # Pass references between controllers (cross-communication)
        self.sources_controller.set_map_controller(self.map_controller)
        self.map_controller.set_sources_controller(self.sources_controller)

        # Setup translations and connect signals
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

    @Slot()
    def _on_open_map(self):
        """ Slot for when the 'Open Map' action is triggered. """
        
        # TODO: Add keys to locale/en.json and locale/pt_BR.json
        # "dialog.open_map.title", "dialog.open_map.filter"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            self.i18n_frontend.t("dialog.open_map.title"), # "Open Map File"
            self.config.get("last_map_directory", "."),
            self.i18n_frontend.t("dialog.open_map.filter") # "SUMO Net Files (*.net.xml)"
        )
        
        if not file_path:
            return # User canceled

        try:
            self.view.status_bar.showMessage(f"Loading map: {file_path}...")
            # 1. Call the Map Importer service
            map_data = self.map_importer.load_file(file_path)
            
            # 2. Update the Model (AppState) using the corrected method
            self.app_state.set_map_data(map_data, file_path)
            
            # 3. Tell MapController to update the View
            self.map_controller.draw_map()
            
            # 4. Tell SourcesController to update (clear) its View
            self.sources_controller.refresh_list()
            
            # TODO: Add key "status_bar.map_loaded" to locale files
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.map_loaded").format(path=file_path))
            
        except Exception as e:
            print(f"Error loading map: {e}")
            error_msg = self.i18n_backend.t("errors.map_importer.invalid_xml").format(error=e)
            self.view.status_bar.showMessage(error_msg)

    @Slot()
    def _on_add_source(self):
        """ Slot for when the 'Add Data Source' action is triggered. """
        
        # TODO: Add keys to locale files
        # "dialog.add_source.title"
        
        folder_path = QFileDialog.getExistingDirectory(
            self.view,
            self.i18n_frontend.t("dialog.add_source.title") # "Select Data Source Folder"
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
                parser_id=analysis.get("file_type") # Use file type as placeholder parser
            )
            
            # 3. Update the Model (AppState)
            self.app_state.add_source(new_source)
            
            # 4. Tell SourcesController to update its View
            self.sources_controller.refresh_list()
            
            # TODO: Add key "status_bar.source_added" to locale files
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.source_added").format(path=folder_path))

        except Exception as e:
            print(f"Error analyzing folder: {e}")
            # TODO: Add key "errors.data_importer.analysis_failed" to backend locale files
            error_msg = self.i18n_backend.t("errors.data_importer.analysis_failed").format(error=e)
            self.view.status_bar.showMessage(error_msg)

    @Slot()
    def _on_save_map(self):
        """ Slot for when the 'Save Mapping' action is triggered. """
        
        map_path = self.app_state.get_map_file_path()
        if not map_path:
            # TODO: Add key "status_bar.save_no_map_error" to locale files
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.save_no_map_error"))
            return # Can't save without a map loaded

        # TODO: Add keys to locale files
        # "dialog.save_map.title", "dialog.save_map.filter"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self.view,
            self.i18n_frontend.t("dialog.save_map.title"), # "Save Mapping File"
            "mapping.db",
            self.i18n_frontend.t("dialog.save_map.filter") # "SQLite Database (*.db)"
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
            
            # TODO: Add key "status_bar.save_success" to locale files
            self.view.status_bar.showMessage(self.i18n_frontend.t("status_bar.save_success").format(path=save_path))
            
        except Exception as e:
            print(f"Error saving file: {e}")
            error_msg = self.i18n_backend.t("errors.persistence.save_failed").format(error=e)
            self.view.status_bar.showMessage(error_msg)