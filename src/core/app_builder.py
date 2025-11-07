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

# File: src/core/app_builder.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Application Builder (SRP Refactor).
#    Handles the "Bootstrapping" responsibility: initializing and
#    connecting all services, models, and controllers.

import os
from PySide6.QtCore import QObject

# Import View
from ui.main_window import MainWindow

# Import Controllers
from src.main_controller import MainController
from src.controllers.map_controller import MapController
from src.controllers.sources_controller import SourcesController

# --- FIX (Req 3): Import the new InfoController ---
from src.controllers.info_controller import InfoController
# --- END FIX ---

# Import Model (State and Services)
from src.domain.app_state import AppState
from src.utils.i18n import I18nManager
from src.utils.config import ConfigManager
from src.services.map_importer import MapImporter
from src.services.data_importer import DataImporter
from src.services.persistence import PersistenceService

# --- SRP Refactor (Map): Import the new MapRenderer ---
from src.core.map_renderer import MapRenderer
# --- END REFACTOR ---


class AppBuilder(QObject):
    """
    Builds the application components and wires them together.
    This class handles the "Bootstrapping" responsibility,
    keeping the MainController clean (SRP).
    """

    def __init__(self, view: MainWindow, app_root: str, parent=None):
        """
        Args:
            view (MainWindow): The passive main view.
            app_root (str): The absolute path to the application root.
        """
        super().__init__(parent)
        self.view = view
        self.app_root = app_root
        print("AppBuilder: Initialized.")

    def build_application(self) -> MainController:
        """
        Creates, initializes, and connects all application components.
        
        Returns:
            MainController: The fully configured main controller.
        """
        print("AppBuilder: Starting application build...")

        # --- 1. Initialize Utilities (Config and i18n) ---
        config_path = os.path.join(self.app_root, "config/settings.json")
        config = ConfigManager(config_path)
        config.load_config()
        
        default_lang = config.get("default_language", "en")
        
        locale_path = os.path.join(self.app_root, "locale")
        locale_backend_path = os.path.join(self.app_root, "locale_backend")
        
        i18n_frontend = I18nManager(locale_path)
        i18n_backend = I18nManager(locale_backend_path)
        
        try:
            i18n_frontend.load_language(default_lang)
            i18n_backend.load_language(default_lang)
            print(f"AppBuilder: Language '{default_lang}' loaded.")
        except Exception as e:
            print(f"CRITICAL: Failed to load language files: {e}")

        # --- 2. Initialize Model (State and Services) ---
        app_state = AppState()
        map_importer = MapImporter()
        data_importer = DataImporter()
        persistence_service = PersistenceService()
        
        # --- 3. Initialize Sub-Controllers and Renderers (SRP Refactor) ---
        
        # 3a. Create the "Painter" (Renderer)
        map_renderer = MapRenderer(
            view=self.view.map_view,
            app_state=app_state
        )

        # 3b. Create the "Brain" (Controller) and inject the "Painter"
        map_controller = MapController(
            view=self.view.map_view, 
            app_state=app_state,
            renderer=map_renderer # Inject the renderer
        )
        
        # 3c. Create the Sources Controller
        sources_controller = SourcesController(
            view=self.view.sources_panel, 
            app_state=app_state
        )
        
        # --- FIX (Req 3): Create the Info Controller ---
        # 3d. Create the Info Controller
        info_controller = InfoController(
            view=self.view.info_panel, # Get the panel from the main window
            app_state=app_state
        )
        # --- END FIX ---


        # --- 4. Wire Components Together ---
        sources_controller.set_map_controller(map_controller)
        map_controller.set_sources_controller(sources_controller)
        
        # --- FIX (Req 3): Inject InfoController into MapController ---
        map_controller.set_info_controller(info_controller)
        # --- END FIX ---

        # --- 5. Initialize Main Controller (Inject Dependencies) ---
        # The MainController is now "clean" and just receives components.
        main_controller = MainController(
            view=self.view,
            app_state=app_state,
            config=config,
            i18n_frontend=i18n_frontend,
            i18n_backend=i18n_backend,
            map_controller=map_controller,
            sources_controller=sources_controller,
            map_importer=map_importer,
            data_importer=data_importer,
            persistence_service=persistence_service
        )
        
        print("AppBuilder: Build complete. Returning configured MainController.")
        return main_controller