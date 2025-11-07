# SFusion (SYNAPSE Fusion) Mapper
#
# Copyright (C) 2025 Gabriel Moraes - Noxfort Labs
#
# Este programa é software livre: pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral Affero GNU como publicada pela
# Free Software Foundation, quer a versão 3 da Licença, ou
# (à sua opção) qualquer versão posterior.
#
# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Veja a
# Licença Pública Geral Affero GNU para mais detalhes.
#
# Deveria ter recebido uma cópia da Licença Pública Geral Affero GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

# File: ui/main_window.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    MainWindow (View). A "casca" principal da UI,
#    baseada em QMainWindow.

import logging
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QMessageBox
)

# Dependências (outras partes da UI ou Utilitários)
from ui.map.map_view import MapView
from ui.sources.sources_panel import SourcesPanel
from src.utils.i18n import I18nManager
# 1. Importar o novo EditorPanel
from ui.editor.editor_panel import EditorPanel


class MainWindow(QMainWindow):
    """
    View principal da aplicação.
    Contém a barra de ferramentas, barra de status e o layout
    que organiza a MapView e o SourcesPanel.
    """
    
    # Sinais que a View emite para o MainController
    open_map_requested = Signal()
    add_source_requested = Signal()
    save_config_requested = Signal()

    def __init__(self, i18n: I18nManager, parent: QWidget | None = None):
        """
        Inicializa a janela principal.
        
        :param i18n: O gestor de internacionalização (tradução).
        :param parent: O widget "Pai" (opcional, normalmente None).
        """
        super().__init__(parent)
        self._i18n = i18n
        
        # 2. Adicionar referência para o novo painel
        self.editor_panel = None
        self.map_view = None
        self.sources_panel = None
        
        # Inicializa a UI
        self._init_ui()
        logging.info("MainWindow (View) inicializada.")

    def _init_ui(self):
        """Constrói os componentes da UI (barra de ferramentas, layout)."""
        
        t = self._i18n.t
        
        self.setWindowTitle(t("main_window.window_title"))
        self.setGeometry(100, 100, 1200, 800)

        # 1. Barra de Ferramentas (Toolbar)
        toolbar = QToolBar(t("main_window.toolbar_name"))
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon) 
        self.addToolBar(toolbar)

        # Ações (Abrir, Adicionar, Salvar)
        action_open = QAction(
            QIcon.fromTheme("document-open"),
            t("main_window.action_open_map"), 
            self
        )
        action_open.setStatusTip(t("main_window.action_open_map_tip"))
        action_open.triggered.connect(self.open_map_requested)
        toolbar.addAction(action_open)

        action_add_source = QAction(
            QIcon.fromTheme("folder-add"),
            t("main_window.action_add_source"), 
            self
        )
        action_add_source.setStatusTip(t("main_window.action_add_source_tip"))
        action_add_source.triggered.connect(self.add_source_requested)
        toolbar.addAction(action_add_source)

        toolbar.addSeparator()

        action_save = QAction(
            QIcon.fromTheme("document-save"),
            t("main_window.action_save_config"), 
            self
        )
        action_save.setStatusTip(t("main_window.action_save_config_tip"))
        action_save.triggered.connect(self.save_config_requested)
        toolbar.addAction(action_save)

        # 2. Barra de Status
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage(t("main_window.status_ready"))

        # 3. Widget Central e Layout (Splitter)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

    # --- Métodos de "Injeção" da View ---

    # 3. Adicionar o "setter" para o novo painel (MÉTODO EM FALTA)
    def set_editor_panel(self, editor_panel: EditorPanel):
        """Recebe e insere o EditorPanel no layout (à esquerda)."""
        self.editor_panel = editor_panel
        # Adiciona o painel editor (será o índice 0)
        self.splitter.addWidget(self.editor_panel)

    def set_map_view(self, map_view: MapView):
        """Recebe e insere a MapView no layout (ao centro)."""
        self.map_view = map_view
        # Adiciona o mapa (será o índice 1)
        self.splitter.addWidget(self.map_view)

    def set_sources_panel(self, sources_panel: SourcesPanel):
        """Recebe e insere o SourcesPanel no layout (à direita)."""
        self.sources_panel = sources_panel
        # Adiciona o painel de fontes (será o índice 2)
        self.splitter.addWidget(self.sources_panel)
        
        # 4. Atualizar os tamanhos e o comportamento de "stretch"
        # Define os tamanhos: (Editor: 250px, Mapa: 700px, Fontes: 250px)
        self.splitter.setSizes([250, 700, 250])
        
        # Define o comportamento de "stretch" (quem cresce)
        self.splitter.setStretchFactor(0, 0) # Painel Editor (não cresce)
        self.splitter.setStretchFactor(1, 1) # Mapa (cresce)
        self.splitter.setStretchFactor(2, 0) # Painel Fontes (não cresce)

    # --- Métodos de Feedback (Chamados pelo MainController) ---

    def show_status_message(self, message: str, timeout: int = 3000):
        """Exibe uma mensagem na barra de status."""
        self.statusBar().showMessage(message, timeout)

    def show_error_message(self, title: str, message: str):
        """Exibe um pop-up de erro crítico."""
        logging.error(f"Mostrando erro para o utilizador: {title} - {message}")
        QMessageBox.critical(self, title, message)

    def show_info_message(self, title: str, message: str):
        """Exibe um pop-up de informação."""
        QMessageBox.information(self, title, message)