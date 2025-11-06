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

# File: src/services/map_importer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Service class (Model) responsible for parsing SUMO .net.xml files
#    and converting them into domain entities (MapData, MapNode, MapEdge).

from lxml import etree
from typing import List, Tuple, Optional

# Import domain entities
from src.domain.entities import MapData, MapNode, MapEdge

class MapImporter:
    """
    Parses SUMO .net.xml files.
    
    This is a "worker" service. It is called by a controller,
    it performs a task (file I/O and parsing), and it returns
    a domain entity (MapData). It holds no state.
    """

    def __init__(self):
        """
        Initializes the MapImporter.
        """
        print("MapImporter: Initialized.")

    def load_file(self, file_path: str) -> MapData:
        """
        Loads and parses a SUMO .net.xml file.
        
        Args:
            file_path (str): The absolute path to the .net.xml file.
            
        Returns:
            MapData: A MapData object containing the parsed nodes and edges.
            
        Raises:
            etree.XMLSyntaxError: If the XML file is malformed.
            FileNotFoundError: If the file_path does not exist.
            Exception: For other unexpected parsing errors.
        """
        print(f"MapImporter: Attempting to parse file: {file_path}")
        
        try:
            # Parse the XML file using lxml
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Parse nodes (junctions) and edges
            nodes = self._parse_nodes(root)
            edges = self._parse_edges(root)
            
            print(f"MapImporter: Parsing complete. Found {len(nodes)} nodes and {len(edges)} edges.")
            
            return MapData(nodes=nodes, edges=edges)

        except etree.XMLSyntaxError as e:
            print(f"MapImporter: Error! Invalid XML syntax in file: {e}")
            raise  # Re-raise for the controller to catch
        except FileNotFoundError as e:
            print(f"MapImporter: Error! File not found: {e}")
            raise  # Re-raise for the controller to catch
        except Exception as e:
            print(f"MapImporter: Error! An unexpected error occurred during parsing: {e}")
            raise  # Re-raise for the controller to catch

    def _parse_nodes(self, root) -> List[MapNode]:
        """
        Parses all <junction> elements from the XML root.
        """
        nodes = []
        # In SUMO .net.xml, nodes are called "junctions"
        for junction in root.findall("junction"):
            node_id = junction.get("id")
            # Internal junctions (often prefixed with ":") might not have x,y
            x_str = junction.get("x")
            y_str = junction.get("y")

            if node_id and x_str and y_str:
                try:
                    nodes.append(MapNode(
                        id=node_id,
                        x=float(x_str),
                        y=float(y_str)
                    ))
                except (ValueError, TypeError):
                    print(f"Warning: Skipping junction '{node_id}' with invalid coordinates.")
        return nodes

    def _parse_edges(self, root) -> List[MapEdge]:
        """
        Parses all <edge> elements from the XML root.
        """
        edges = []
        for edge in root.findall("edge"):
            edge_id = edge.get("id")
            from_node = edge.get("from")
            to_node = edge.get("to")
            shape_str = edge.get("shape")
            
            # We need all attributes to create a valid edge
            if not (edge_id and from_node and to_node and shape_str):
                continue

            try:
                shape_coords = self._parse_shape(shape_str)
                edges.append(MapEdge(
                    id=edge_id,
                    from_node=from_node,
                    to_node=to_node,
                    shape=shape_coords
                ))
            except Exception as e:
                print(f"Warning: Skipping edge '{edge_id}' due to shape parsing error: {e}")
                
        return edges

    def _parse_shape(self, shape_str: str) -> List[Tuple[float, float]]:
        """
        Converts a SUMO shape string "x1,y1 x2,y2 ..." into a list of tuples.
        """
        coordinates = []
        pairs = shape_str.split(" ")
        for pair in pairs:
            xy = pair.split(",")
            if len(xy) == 2:
                try:
                    x = float(xy[0])
                    y = float(xy[1])
                    coordinates.append((x, y))
                except ValueError:
                    # Silently skip malformed pairs
                    print(f"Warning: Skipping invalid coordinate pair '{pair}' in shape.")
            else:
                print(f"Warning: Skipping invalid shape part '{pair}'.")
        return coordinates