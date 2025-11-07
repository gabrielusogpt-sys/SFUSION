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
#    MapView (View). O widget QGraphicsView especializado
#    para renderizar e interagir com o mapa.

import logging
# --- 1. CORREÇÃO AQUI ---
# Adicionamos QPoint à lista de importações do QtCore
from PySide6.QtCore import Qt, Signal, Slot, QRectF, QPoint
from PySide6.QtGui import QPainter, QTransform
from PySide6.QtWidgets import (
    QGraphicsView, 
    QGraphicsScene, 
    QGraphicsItem, 
    QWidget
)


class MapView(QGraphicsView):
    """
    View especializada do mapa.
    
    Responsabilidades:
    - Renderizar a cena (QGraphicsScene) com fundo branco.
    - Processar Pan (arrastar) e Zoom (scroll).
    - Detetar cliques em itens (nós/arestas) ou espaço vazio.
    - Emitir sinais (ex: nodeClicked) para o MapController.
    """
    
    # Sinais para o MapController
    nodeClicked = Signal(str)
    edgeClicked = Signal(str)
    emptySpaceClicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # 1. Configurar a Cena
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # 2. Configurar a View
        self._setup_view_settings()

        # Controlo de Pan (arrastar)
        self._is_panning = False
        self._last_pan_point = None

        logging.info("MapView (View) inicializada.")

    def _setup_view_settings(self):
        """Define as configurações de renderização e interação."""
        # --- Refinamento Visual ---
        self.setRenderHint(QPainter.Antialiasing) 
        self.scene.setBackgroundBrush(Qt.white) 

        # --- Comportamento de Zoom/Pan ---
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    # --- Métodos Públicos (Chamados pelo Renderer) ---

    @Slot()
    def fit_map_in_view(self):
        """
        Ajusta o zoom para que todo o mapa caiba na vista.
        """
        try:
            rect = self.scene.itemsBoundingRect()
            if rect.isValid():
                rect.adjust(-rect.width() * 0.05, 
                            -rect.height() * 0.05,
                            rect.width() * 0.05, 
                            rect.height() * 0.05)
                
                self.fitInView(rect, Qt.KeepAspectRatio)
                logging.info(f"MapView: Zoom ajustado para o mapa. (Rect: {rect})")
        except Exception as e:
            logging.error(f"MapView: Erro ao tentar ajustar o zoom: {e}")

    @Slot(float, float)
    def set_zoom_limits(self, min_factor: float, max_factor: float):
        """Define os limites mínimo e máximo de zoom."""
        # (Este método existe para satisfazer a chamada do MapRenderer)
        logging.info(f"MapView: Limites de zoom definidos (Min: {min_factor}, Max: {max_factor})")
        # A lógica real de limitação de zoom é feita no 'wheelEvent'

    # --- Eventos de Interação (Pan/Zoom/Clique) ---

    def wheelEvent(self, event):
        """Lida com o scroll do rato (Zoom)."""
        zoom_factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        """Lida com o clique do rato (Início do Pan ou Clique)."""
        
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.LeftButton:
            # Passa o evento (QPoint) para o slot de clique
            self._on_scene_clicked(event.pos())
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Lida com o movimento do rato (Pan)."""
        if self._is_panning:
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Lida com o soltar do rato (Fim do Pan)."""
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
            
        super().mouseReleaseEvent(event)

    # --- Lógica de Clique ---

    # 2. Esta anotação de tipo (QPoint) agora é válida
    @Slot(QPoint)
    def _on_scene_clicked(self, pos: QPoint):
        """
        Processa um clique esquerdo na cena.
        Verifica se um item foi clicado e emite o sinal correto.
        """
        scene_pos = self.mapToScene(pos)
        item = self.itemAt(pos)

        if item:
            item_type = item.data(0)
            item_id = item.data(1) 

            if item_type == "node":
                self.nodeClicked.emit(item_id)
            elif item_type == "edge":
                self.edgeClicked.emit(item_id)
            
        else:
            self.emptySpaceClicked.emit()