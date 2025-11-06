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

# File: src/domain/app_state.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Defines the AppState class, which acts as the "single source of truth"
#    for the application's runtime state. It holds the currently loaded
#    map data and the list of configured data sources.

from typing import Optional, Dict, List
from .entities import MapData, DataSource

class AppState:
    """
    Holds the runtime state of the application (Model).

    This class is the "single source of truth". Controllers modify this
    state, and then update the Views based on this state.
    It is a pure Python object, not tied to Qt.
    """
    
    def __init__(self):
        """
        Initializes the application state.
        """
        # The currently loaded map data (nodes, edges)
        self.map_data: Optional[MapData] = None
        # The path of the loaded map file
        self.map_file_path: Optional[str] = None
        
        # The list of data sources, indexed by their unique ID
        self.data_sources: Dict[str, DataSource] = {}
        
        print("AppState: Initialized (Single Source of Truth).")

    # --- Map State Methods ---

    def set_map_data(self, map_data: MapData, map_path: str):
        """
        Sets the loaded map data and clears any old source mappings.
        Called by MainController after a successful map load.
        """
        print(f"AppState: Setting map data ({len(map_data.nodes)} nodes, {len(map_data.edges)} edges).")
        print(f"AppState: Setting map path: {map_path}")
        
        self.map_data = map_data
        self.map_file_path = map_path

        # When a new map is loaded, old associations are invalid
        self.clear_all_sources()

    def get_map_data(self) -> Optional[MapData]:
        """ Returns the currently loaded map data. """
        return self.map_data
        
    def get_map_file_path(self) -> Optional[str]:
        """ Returns the file path of the currently loaded map. """
        return self.map_file_path

    # --- Data Source State Methods ---

    def add_source(self, data_source: DataSource):
        """
        Adds a new data source to the state.
        Called by SourcesController.
        """
        if data_source.id in self.data_sources:
            print(f"Warning: Source ID {data_source.id} already exists. Overwriting.")
        
        print(f"AppState: Adding source '{data_source.path}' (ID: {data_source.id}).")
        self.data_sources[data_source.id] = data_source
        
    def get_source(self, source_id: str) -> Optional[DataSource]:
        """
        Retrieves a single data source by its unique ID.
        """
        return self.data_sources.get(source_id)

    def get_all_sources(self) -> List[DataSource]:
        """
        Returns a list of all current data sources.
        """
        return list(self.data_sources.values())

    def clear_all_sources(self):
        """
        Removes all data sources from the state.
        """
        print("AppState: Clearing all data sources.")
        self.data_sources.clear()