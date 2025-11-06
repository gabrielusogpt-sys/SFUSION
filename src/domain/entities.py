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

# File: src/domain/entities.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Defines the core business logic data structures (entities)
#    for the application, such as Node, Edge, and DataSource.
#    These are "dumb" data containers used by the Model.

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum, auto
import uuid

class SourceType(Enum):
    """ Defines if a data source is global or locally mapped. """
    GLOBAL = auto()
    LOCAL = auto()

class ElementType(Enum):
    """ Defines the type of map element for association. """
    NODE = auto()
    EDGE = auto()

# --- Map Entities (Immutable) ---

@dataclass(frozen=True)
class MapNode:
    """ Represents a single node (junction) from the map. """
    id: str
    x: float
    y: float

@dataclass(frozen=True)
class MapEdge:
    """ 
    Represents a single edge (road) from the map. 
    'shape' is the list of (x,y) coordinates that define the road's geometry.
    """
    id: str
    from_node: str
    to_node: str
    shape: List[Tuple[float, float]]

@dataclass(frozen=True)
class MapData:
    """ A container for all parsed map data. """
    nodes: List[MapNode]
    edges: List[MapEdge]

# --- Data Source Entities (Mutable) ---

@dataclass
class MappingAssociation:
    """ Represents the association of a source to one map element. """
    element_id: str
    element_type: ElementType

@dataclass
class DataSource:
    """
    Represents a single data source (e.g., a folder of CSVs)
    and its mapping configuration. This is a mutable entity that
    the user edits via the UI.
    """
    path: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType = SourceType.GLOBAL
    parser_id: Optional[str] = None # e.g., "csv_parser_A"
    association: Optional[MappingAssociation] = None

    def set_local_association(self, element_id: str, element_type: ElementType):
        """ Helper method to set this source as Local and define its association. """
        self.source_type = SourceType.LOCAL
        self.association = MappingAssociation(
            element_id=element_id, 
            element_type=element_type
        )
    
    def set_global(self):
        """ Helper method to set this source as Global and clear association. """
        self.source_type = SourceType.GLOBAL
        self.association = None

    @property
    def is_local(self) -> bool:
        """ Check if the source type is Local. """
        return self.source_type == SourceType.LOCAL