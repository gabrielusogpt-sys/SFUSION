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

# File: src/domain/entities.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Data Entities (Model). Defines the core data structures
#    used by the application (e.g., DataSource, MapNode).
#    These are simple dataclasses.

from dataclasses import dataclass, field
from enum import Enum
import uuid
from typing import List, Tuple


# --- FIX: Moved AssociationType definition UP ---
# It must be defined *before* the DataSource class, which uses it
# for type hinting and default values.
class AssociationType(str, Enum):
    """ Defines how a DataSource is associated with the map. """
    UNASSOCIATED = "UNASSOCIATED"
    GLOBAL = "GLOBAL" # Associated with the whole map
    LOCAL = "LOCAL"   # Associated with a specific node
# --- END FIX ---


@dataclass
class DataSource:
    """
    Entity (Model) representing a single data source.
    """
    path: str
    id: str = field(default_factory=lambda: f"src_{uuid.uuid4().hex[:8]}")
    parser_id: str | None = None
    
    # This type hint and default value requires AssociationType
    # to be defined *before* this class.
    association_type: AssociationType = AssociationType.UNASSOCIATED
    associated_node_id: str | None = None
    
    # TODO: Add fields for column mapping, etc.
    # mapped_columns: Dict[str, str] = field(default_factory=dict)


@dataclass
class MapNode:
    """
    Entity (Model) representing a single map node (junction).
    """
    id: str
    x: float
    y: float # Y-coordinate is inverted (Qt style)
    
    # --- FIX: Add fields for new features ---
    # Field to store the junction type (e.g., "internal", "priority")
    # This will be used to solve the "Vários Nós" problem (Req 2).
    node_type: str = "unknown"
    
    # Field to store the user-defined "real name" (Req 3).
    real_name: str | None = None
    # --- END FIX ---


@dataclass
class MapEdge:
    """
    Entity (Model) representing a single map edge (road).
    """
    id: str
    from_node: str
    to_node: str
    shape: List[Tuple[float, float]] = field(default_factory=list)
    
    # --- FIX: Add field for new features ---
    # Field to store the user-defined "real name" (Req 3).
    real_name: str | None = None
    # --- END FIX ---