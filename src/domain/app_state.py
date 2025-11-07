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

# File: src/domain/app_state.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    AppState (Model). The "Single Source of Truth" for the application.
#    It holds the map data and source list in memory.
#    It is completely independent of Qt/UI.

from typing import Dict, List, Any, Iterable

# FIX: Changed import to be absolute from the project root (src.)
# FIX (Req 3): Import MapEdge as well
from src.domain.entities import DataSource, MapNode, MapEdge
# --- END FIX ---


class AppState:
    """
    Holds the application's in-memory state.
    This is the "Single Source of Truth" (Model).
    """
    def __init__(self):
        # The list of all loaded data sources
        self._sources: Dict[str, DataSource] = {}
        
        # The parsed map data
        self._map_data: Dict[str, Any] = {}
        self._map_file_path: str | None = None
        
        # Cache for quick node lookups
        self._nodes_by_id: Dict[str, MapNode] = {}
        
        # --- FIX (Req 3): Add cache for quick edge lookups ---
        self._edges_by_id: Dict[str, MapEdge] = {}
        # --- END FIX ---

    # --- Map Data Methods ---

    def set_map_data(self, map_data: Dict[str, Any], file_path: str):
        """
        Sets the loaded map data, replacing any existing data.
        
        Args:
            map_data (Dict): The dictionary from MapImporter
                             (containing 'nodes' and 'edges').
            file_path (str): The path to the .net.xml file.
        """
        self._map_data = map_data
        self._map_file_path = file_path
        
        # Clear existing data sources, as they are map-specific
        self.clear_all_sources()
        
        # Build the node cache
        self._nodes_by_id.clear()
        for node in map_data.get("nodes", []):
            self._nodes_by_id[node.id] = node
            
        print(f"AppState: Map data set. {len(self._nodes_by_id)} nodes cached.")

        # --- FIX (Req 3): Build the edge cache ---
        self._edges_by_id.clear()
        for edge in map_data.get("edges", []):
            self._edges_by_id[edge.id] = edge
        print(f"AppState: {len(self._edges_by_id)} edges cached.")
        # --- END FIX ---


    def get_map_data(self) -> Dict[str, Any]:
        """ Returns the full map data dictionary. """
        return self._map_data

    def get_map_file_path(self) -> str | None:
        """ Returns the path to the loaded .net.xml file. """
        return self._map_file_path
        
    def get_node_by_id(self, node_id: str) -> MapNode | None:
        """
        Gets a single MapNode from the cache by its ID.
        """
        return self._nodes_by_id.get(node_id)

    # --- FIX (Req 3): Add method to get edge by ID ---
    def get_edge_by_id(self, edge_id: str) -> MapEdge | None:
        """
        Gets a single MapEdge from the cache by its ID.
        """
        return self._edges_by_id.get(edge_id)
    # --- END FIX ---

    # --- Data Source Methods ---

    def add_source(self, source: DataSource):
        """
        Adds a new data source to the state.
        
        Args:
            source (DataSource): The new DataSource entity to add.
        """
        if source.id in self._sources:
            print(f"Warning: Source with ID {source.id} already exists. Overwriting.")
        
        self._sources[source.id] = source
        print(f"AppState: Source '{source.id}' added.")

    def get_source_by_id(self, source_id: str) -> DataSource | None:
        """
        Gets a single data source by its unique ID.
        """
        return self._sources.get(source_id)

    def get_all_sources(self) -> Iterable[DataSource]:
        """
        Returns an iterable of all loaded DataSource entities.
        """
        return self._sources.values()

    def clear_all_sources(self):
        """
        Removes all data sources from memory.
        """
        count = len(self._sources)
        self._sources.clear()
        print(f"AppState: Cleared {count} data sources.")