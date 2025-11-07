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

# File: sfusion.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Main application entry point.
#    Initializes the Qt Application, View (passive), and
#    uses the AppBuilder (Core) to create the Controller.

import sys
import os

# --- FIX: Robust Pathing ---
# Calculate the application's root directory (where sfusion.py lives)
# This ensures that relative paths for 'locale' and 'config' work
# regardless of where the script is executed from (e.g., from VS Code).
APP_ROOT = os.path.abspath(os.path.dirname(__file__))

# --- FIX: Add the Project ROOT to the path ---
# This allows for absolute imports like 'from src.main_controller...'
# and 'from ui.main_window...'
sys.path.insert(0, APP_ROOT)
# --- END FIX ---


from PySide6.QtWidgets import QApplication

# Import the View
from ui.main_window import MainWindow

# --- FIX: Import the AppBuilder, not the MainController ---
# The AppBuilder now handles the creation of the MainController (SRP)
from src.core.app_builder import AppBuilder
# --- END FIX ---

if __name__ == "__main__":
    
    print(f"SFusion Mapper: Initializing...")
    print(f"SFusion Mapper: Application Root Path: {APP_ROOT}")
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # 1. Create the View
    print("SFusion Mapper: Creating View (MainWindow)...")
    view = MainWindow()
    
    # --- FIX: Use the AppBuilder to construct the application ---
    # 2. Create the Builder
    print("SFusion Mapper: Creating AppBuilder (src/core/app_builder.py)...")
    builder = AppBuilder(view=view, app_root=APP_ROOT)

    # 3. Build the application
    # The builder creates all services, models, controllers,
    # injects them, and returns the configured main_controller.
    print("SFusion Mapper: Building application components...")
    controller = builder.build_application()
    # --- END FIX ---
    
    # 4. Show the View
    print("SFusion Mapper: Showing main window...")
    view.show()
    
    # 5. Run the application
    print("SFusion Mapper: Starting event loop (app.exec())...")
    sys.exit(app.exec())