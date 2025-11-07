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

# File: src/services/map_importer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Map Importer (Service). Parses a .net.xml file (Model logic).
#    It is completely independent of Qt/UI.

from lxml import etree
from typing import Dict, List, Any

# FIX: Changed import to be absolute from the project root (src.)
from src.domain.entities import MapNode, MapEdge
# --- END FIX ---


class MapImporter:
    """
    Service class responsible for parsing SUMO .net.xml files.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        # We can pre-compile XPath expressions if performance is critical,
        # but for a "Day Zero" tool, direct parsing is fine.
        pass

    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Loads and parses a .net.xml file.
        
        Args:
            file_path (str): The absolute path to the .net.xml file.
            
        Returns:
            Dict[str, Any]: A dictionary containing lists of 'nodes' and 'edges'.
            
        Raises:
            Exception: If the file is invalid XML or structure is missing.
        """
        print(f"MapImporter: Parsing {file_path}...")
        
        try:
            # Parse the XML file
            # lxml.etree.parse can natively handle .gz files
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            nodes = []
            edges = []

            # --- FIX: Load ALL junctions (nodes), not just 'internal' ---
            # We want to render the full map for visual context.
            for junction in root.xpath("//junction"):
            # --- END FIX ---
                node_id = junction.get("id")
                x = float(junction.get("x"))
                y = float(junction.get("y"))
                
                # --- FIX: Read the node type (for Problem 2) ---
                # Get the 'type' attribute (e.g., "internal", "priority")
                node_type = junction.get("type", "unknown")
                # --- END FIX ---
                
                # We invert 'y' because Qt's Y-axis is inverted (0 is top)
                # --- FIX: Pass the node_type to the entity ---
                nodes.append(MapNode(id=node_id, x=x, y=-y, node_type=node_type))
                # --- END FIX ---

            # --- FIX: Load ALL edges, not just non-internal ones ---
            # We want to render the full map.
            for edge in root.xpath("//edge"):
            # --- END FIX ---
                edge_id = edge.get("id")
                from_node = edge.get("from")
                to_node = edge.get("to")
                shape_str = edge.get("shape")
                
                shape_coords = []
                if shape_str:
                    try:
                        # Shape is "x1,y1 x2,y2 x3,y3 ..."
                        points = shape_str.split(' ')
                        for point in points:
                            coords = point.split(',')
                            x = float(coords[0])
                            y = float(coords[1])
                            # We invert 'y' because Qt's Y-axis is inverted
                            shape_coords.append((x, -y))
                    except Exception as e:
                        print(f"Warning: Could not parse shape for edge {edge_id}: {e}")
                        shape_coords = [] # Fallback
                
                edges.append(MapEdge(
                    id=edge_id, 
                    from_node=from_node, 
                    to_node=to_node,
                    shape=shape_coords
                ))
            
            print(f"MapImporter: Parsing complete. Found {len(nodes)} total nodes and {len(edges)} total edges.")
            
            return {
                "nodes": nodes,
                "edges": edges
            }

        except etree.XMLSyntaxError as e:
            print(f"CRITICAL: XML Syntax Error in {file_path}. {e}")
            raise Exception(f"File is not valid XML: {e}")
        except Exception as e:
            print(f"CRITICAL: Failed to parse map file. {e}")
            raise Exception(f"Unknown error during map parsing: {e}")