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

# File: src/main_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    MainController (Controller). O "cérebro" principal
#    para a MainWindow.

import logging
import os
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog

# 1. Importar os tipos corretos
from ui.main_window import MainWindow
from src.services.map_importer import MapImporter
from src.services.data_importer import DataImporter
from src.services.persistence import PersistenceService
from src.utils.i18n import I18nManager


class MainController(QObject):
    """
    Controlador principal. Gere as ações da barra de ferramentas (View)
    e orquestra os Serviços (Serviços).
    (Refatorado para SRP)
    """

    # --- 2. Alteração Principal: Corrigir o __init__ ---
    def __init__(
        self,
        main_window: MainWindow,
        map_importer: MapImporter,
        data_importer: DataImporter,
        persistence_service: PersistenceService,
        i18n: I18nManager
    ):
        """
        Inicializa o controlador principal.
        
        :param main_window: A View (Janela Principal)
        :param map_importer: O Serviço para carregar mapas
        :param data_importer: O Serviço para carregar fontes
        :param persistence_service: O Serviço para salvar
        :param i18n: O gestor de internacionalização
        """
        # 3. Chamar super() sem argumentos
        super().__init__()
        
        # 4. Armazenar as referências (Injeção de Dependência)
        self._view = main_window
        self._map_importer = map_importer
        self._data_importer = data_importer
        self._persistence = persistence_service
        self._i18n = i18n

        # Define o diretório inicial para diálogos
        self._current_path = os.path.expanduser("~") # Pasta home do utilizador
        
        logging.info("MainController (Controlador) inicializado.")

    def setup_connections(self):
        """Conecta os sinais da MainWindow aos slots deste controlador."""
        self._view.open_map_requested.connect(self._on_open_map)
        self._view.add_source_requested.connect(self._on_add_source)
        self._view.save_config_requested.connect(self._on_save_config)

    # --- Slots Privados (Ouvem a View) ---

    @Slot()
    def _on_open_map(self):
        """Chamado pelo sinal 'open_map_requested' da View."""
        t = self._i18n.t
        file_path, _ = QFileDialog.getOpenFileName(
            self._view,
            t("dialog.open_map.title"),
            self._current_path,
            t("dialog.open_map.filter")
        )
        
        if file_path:
            self._current_path = os.path.dirname(file_path) # Atualiza o caminho
            try:
                # 5. Delega o trabalho ao Serviço
                self._map_importer.load_map(file_path)
                
                # 6. Atualiza a View (feedback)
                msg = t("main_window.status_map_loaded", 
                        name=os.path.basename(file_path))
                self._view.show_status_message(msg)
                
            except Exception as e:
                # (Idealmente, o Worker emitiria um sinal de falha)
                msg = t("dialog.error.generic_load", error=str(e))
                self._view.show_error_message(t("dialog.error.title"), msg)

    @Slot()
    def _on_add_source(self):
        """Chamado pelo sinal 'add_source_requested' da View."""
        t = self._i18n.t
        folder_path = QFileDialog.getExistingDirectory(
            self._view,
            t("dialog.add_source.title"),
            self._current_path
        )
        
        if folder_path:
            self._current_path = folder_path # Atualiza o caminho
            try:
                # 5. Delega o trabalho ao Serviço
                self._data_importer.add_data_source(folder_path)
                
                # 6. Atualiza a View (feedback)
                # (O AppState emitirá um sinal que o SourcesController ouvirá)
                msg = t("main_window.status_source_added", 
                        name=os.path.basename(folder_path))
                self._view.show_status_message(msg)
                
            except Exception as e:
                msg = t("dialog.error.generic_load", error=str(e))
                self._view.show_error_message(t("dialog.error.title"), msg)

    @Slot()
    def _on_save_config(self):
        """Chamado pelo sinal 'save_config_requested' da View."""
        t = self._i18n.t
        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            t("dialog.save_config.title"),
            self._current_path,
            t("dialog.save_config.filter")
        )
        
        if file_path:
            self._current_path = os.path.dirname(file_path) # Atualiza o caminho
            try:
                # 5. Delega o trabalho ao Serviço
                self._persistence.save_configuration(file_path)
                
                # 6. Atualiza a View (feedback)
                msg = t("main_window.status_config_saved", 
                        name=os.path.basename(file_path))
                self._view.show_status_message(msg)
                
            except Exception as e:
                msg = t("dialog.error.generic_save", error=str(e))
                self._view.show_error_message(t("dialog.error.title"), msg)