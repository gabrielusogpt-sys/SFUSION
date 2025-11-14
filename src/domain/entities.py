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
from typing import List, Tuple, Any # Adicionar Any para file_types


# (Definição de Enum - movida para cima no seu ficheiro, o que está correto)
class AssociationType(str, Enum):
    """ Defines how a DataSource is associated with the map. """
    UNASSOCIATED = "UNASSOCIATED"
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"


@dataclass
class DataSource:
    """
    Entity (Model) representing a single data source.
    """
    path: str
    
    # --- 1. CORREÇÃO PRINCIPAL ---
    # Adicionamos o campo 'name' que o DataImporter está a tentar passar.
    name: str
    
    # Lista de tipos de ficheiros detetados (ex: ["JSON", "CSV"])
    file_types: list[str] = field(default_factory=list)
    
    # (Campos do seu ficheiro original, mantidos)
    id: str = field(default_factory=lambda: f"src_{uuid.uuid4().hex[:8]}")
    parser_id: str | None = None
    
    association_type: AssociationType = AssociationType.UNASSOCIATED
    
    # Alterado de 'associated_node_id' para um nome genérico
    associated_element_id: str | None = None
    
    # (Campos da nossa arquitetura - fundidos com os seus)
    # A 'file_types' já está acima.
    # A 'association_type' já está acima.


@dataclass
class MapNode:
    """
    Entity (Model) representing a single map node (junction).
    """
    id: str
    x: float
    y: float
    
    # (Campo do seu ficheiro original, mantido)
    node_type: str = "unknown"
    
    # (Campo do seu ficheiro original, mantido)
    real_name: str | None = None


@dataclass
class MapEdge:
    """
    Entity (Model) representing a single map edge (road).
    """
    id: str
    
    # (Campos do seu ficheiro original, mantidos)
    from_node: str
    to_node: str
    shape: List[Tuple[float, float]] = field(default_factory=list)
    
    # (Campo do seu ficheiro original, mantido)
    real_name: str | None = None