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

# File: ui/map/map_view.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Map View (View). A QGraphicsView specialized for panning,
#    zooming, and interacting with the map scene. It is a "dumb"
#    component that emits signals for the controller.

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QTransform, QMouseEvent, QContextMenuEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu

class MapView(QGraphicsView):
    """
    Custom QGraphicsView for map display and interaction.
    Emits signals on user actions for the controller to handle.
    """
    
    # --- Signals ---
    # Emitted when a node (QGraphicsEllipseItem) is clicked
    nodeClicked = Signal(str)
    
    # FIX: Define the missing signal for empty space clicks
    # Emitted when the empty background of the scene is clicked
    emptySpaceClicked = Signal()
    # --- END FIX ---
    
    
    def __init__(self, parent=None):
        """
        Constructor.
        """
        super().__init__(parent)
        
        # 1. Setup Scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # 2. Setup Render Hints
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 3. Setup Interaction
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # 4. Setup Context Menu
        # We handle this manually to pass the correct coordinates
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    # --- Public API (Used by Controller) ---

    def clear_scene(self):
        """ Clears all items from the graphics scene. """
        self.scene.clear()

    def add_item_to_scene(self, item: QGraphicsItem):
        """ Adds a QGraphicsItem (node, edge) to the scene. """
        self.scene.addItem(item)
        
    def fit_to_scene(self):
        """
        Zooms and centers the view to fit the entire scene contents.
        """
        if not self.scene.items():
            return
        
        # Reset transform to avoid scaling issues
        self.setTransform(QTransform()) 
        
        # Get the bounding rectangle of all items
        rect = self.scene.itemsBoundingRect()
        
        # Fit the view to that rectangle
        self.fitInView(rect, Qt.KeepAspectRatio)

    def show_context_menu(self, menu: QMenu, global_pos: QPoint):
        """
        Displays a context menu at the given global position.
        Called by the MapController.
        """
        menu.exec_(global_pos)

    # --- Event Handlers (Internal Logic) ---

    def wheelEvent(self, event):
        """
        Handles mouse wheel events for zooming.
        """
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Check wheel direction
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        # Apply scaling
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events to detect item clicks.
        """
        # --- Handle Left-Click ---
        if event.button() == Qt.LeftButton:
            # Get the item at the click position
            item = self.itemAt(event.pos())
            
            if item and item.data(0): # data(0) holds the Node ID
                # Clicked on a node
                node_id = item.data(0)
                self.nodeClicked.emit(node_id)
            else:
                # FIX: Clicked on empty space
                self.emptySpaceClicked.emit()
                # --- END FIX ---
        
        # Pass the event to the base class (for panning)
        super().mousePressEvent(event)
        
    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Handles right-click events to show the context menu.
        """
        # We emit a custom signal with the global position
        # The controller will build and show the menu
        self.customContextMenuRequested.emit(event.globalPos())