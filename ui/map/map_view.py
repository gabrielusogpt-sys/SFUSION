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

# File: ui/map/map_view.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Defines the MapView class (QGraphicsView), the main component
#    responsible for rendering the 2D map and handling user interaction
#    (zoom, pan, click). This file includes drawing logic and click signals.

import sys
from typing import List, Tuple  # <-- CORRECTION IS HERE
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PySide6.QtWidgets import (
    QApplication, 
    QGraphicsView, 
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsItem
)

# Custom data roles to store metadata inside QGraphicsItems
ITEM_ID_ROLE = Qt.UserRole + 0
ITEM_TYPE_ROLE = Qt.UserRole + 1

class MapView(QGraphicsView):
    """
    The MapView (View) component.
    
    This class provides the visual rendering surface for the network map.
    It handles user interactions like zooming and panning.
    It is a "dumb" component that simply renders what the MapController
    tells it to render and emits signals upon user interaction.
    """
    
    # --- Signals ---
    # Emits the string ID of the map element that was clicked
    nodeClicked = Signal(str)
    edgeClicked = Signal(str)
    
    def __init__(self, parent=None):
        """
        MapView constructor.
        """
        super().__init__(parent)

        # The scene holds all the 2D items (nodes, edges)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Set up the view properties
        self.setup_view()

    def setup_view(self):
        """
        Configures the rendering and interaction properties of the view.
        """
        # Enable Anti-aliasing for smooth lines and curves
        self.setRenderHint(QPainter.Antialiasing)
        
        # Improve performance
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

        # Set the anchor point for transformations (zoom) to the mouse cursor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # Enable panning by dragging the mouse
        self.setDragMode(QGraphicsView.ScrollHandDrag) 

        # Enable mouse tracking to show coordinates or hover effects later
        self.setMouseTracking(True)
        
        # Set a placeholder scene rectangle (will be updated when map loads)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

    def wheelEvent(self, event):
        """
        Overrides the mouse wheel event to handle zooming.
        """
        zoom_factor = 1.15 # Zoom in/out factor
        
        if event.angleDelta().y() > 0:
            # Zoom In
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom Out
            self.scale(1.0 / zoom_factor, zoom_factor)
            
    # --- Event Overrides (for Click Handling) ---
    
    def mousePressEvent(self, event):
        """
        Overrides the mouse press event to detect clicks on items.
        """
        # Get the item at the click position
        item = self.itemAt(event.pos())
        
        if item:
            item_id = item.data(ITEM_ID_ROLE)
            item_type = item.data(ITEM_TYPE_ROLE)
            
            # If the item has our custom data, emit a signal
            if item_id and item_type == "NODE":
                self.nodeClicked.emit(item_id)
            elif item_id and item_type == "EDGE":
                self.edgeClicked.emit(item_id)

        # IMPORTANT: Call the parent's event handler
        # This allows panning (ScrollHandDrag) to still work.
        super().mousePressEvent(event)
            
    # --- Public Methods (API for the Controller) ---
    
    def clear_map(self):
        """
        Clears all items from the map scene.
        Called by the controller before loading a new map.
        """
        self.scene.clear()

    def draw_node(self, node_id: str, x: float, y: float, size: int = 5):
        """
        Draws a single node (junction) on the map as an ellipse.
        
        Args:
            node_id (str): The unique ID of the node (e.g., "J10").
            x (float): The x-coordinate.
            y (float): The y-coordinate.
            size (int): The diameter of the node circle.
        """
        # QGraphicsEllipseItem draws from top-left, so offset by half size
        top_left_x = x - (size / 2)
        top_left_y = y - (size / 2)
        
        # Create the graphical item
        brush = QBrush(QColor("#e74c3c")) # Red
        pen = QPen(QColor("#2c3e50"), 0.5) # Dark border
        ellipse = self.scene.addEllipse(top_left_x, top_left_y, size, size, pen, brush)
        
        # Store our custom metadata (ID and Type) inside the item
        ellipse.setData(ITEM_ID_ROLE, node_id)
        ellipse.setData(ITEM_TYPE_ROLE, "NODE")

    def draw_edge(self, edge_id: str, shape: List[Tuple[float, float]]):
        """
        Draws a single edge (road) on the map as a path.
        
        Args:
            edge_id (str): The unique ID of the edge (e.g., "E5").
            shape (List[tuple]): A list of (x, y) coordinates defining the line.
        """
        if not shape:
            return # Cannot draw an edge with no shape

        # A QPainterPath can draw a line with multiple points
        path = QPainterPath()
        path.moveTo(shape[0][0], shape[0][1])
        for (x, y) in shape[1:]:
            path.lineTo(x, y)
        
        # Create the graphical item
        pen = QPen(QColor("#3498db"), 1.0) # Blue
        item = self.scene.addPath(path, pen)
        
        # Store our custom metadata (ID and Type) inside the item
        item.setData(ITEM_ID_ROLE, edge_id)
        item.setData(ITEM_TYPE_ROLE, "EDGE")
        
    def fit_to_scene(self):
        """
        Adjusts the view's zoom to fit all items in the scene.
        Called by the controller after a map is drawn.
        """
        rect = self.scene.itemsBoundingRect()
        if not rect.isNull():
            # Add a small margin (e.g., 10%)
            rect.adjust(-rect.width()*0.05, -rect.height()*0.05, 
                         rect.width()*0.05,  rect.height()*0.05)
            self.fitInView(rect, Qt.KeepAspectRatio)


# --- This block allows you to run this file directly for testing ---
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    view = MapView()
    view.setWindowTitle("MapView Test (Updated)")
    view.resize(800, 600)
    
    # Add dummy data using the new API
    view.draw_node("J1", 0, 0, 10)
    view.draw_node("J2", 100, 50, 10)
    view.draw_edge("E1", [(0, 0), (50, 25), (100, 50)])
    view.draw_edge("E2", [(0, 0), (0, 100), (50, 150)])
    
    # Test the fit_to_scene method
    view.fit_to_scene()
    
    # Connect signals to a simple print function for testing
    view.nodeClicked.connect(lambda node_id: print(f"TEST: Node clicked: {node_id}"))
    view.edgeClicked.connect(lambda edge_id: print(f"TEST: Edge clicked: {edge_id}"))
    
    view.show()
    sys.exit(app.exec())