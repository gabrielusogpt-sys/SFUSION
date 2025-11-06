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
#    Main entry point for the SFusion Mapper application.
#    This file initializes the QApplication, the main window (View),
#    and the main controller, connecting them together.

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Import the main controller from its new location
from src.main_controller import MainController

# TODO: Import Model components when they are created
# from src.domain.app_state import AppState

def main():
    """
    Main application function.
    Initializes the application, the main view, and the main controller.
    """
    app = QApplication(sys.argv)
    
    # --- View Layer ---
    # 1. Create the main window (the View)
    window = MainWindow()
    
    # --- Model Layer (placeholder) ---
    # TODO: 2. Create the application state
    # app_state = AppState()

    # --- Controller Layer (Initialization) ---
    # 3. Create the main controller and pass it the view (and model)
    #    The controller's __init__ will handle connecting signals.
    main_controller = MainController(view=window)
    
    # --- Start Application ---
    # The controller (when implemented) will be responsible for
    # setting the final window title, loading translations, etc.
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    # This is the main entry point of the application
    main()