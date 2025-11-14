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
# junto com este programa. If not, see <https://www.gnu.org/licenses/>.

# File: src/main_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    MainController (Controller). O "cérebro" principal
#    para a MainWindow.

import logging
import os
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

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
        super().__init__()
        
        self._view = main_window
        self._map_importer = map_importer
        self._data_importer = data_importer
        self._persistence = persistence_service
        self._i18n = i18n

        self._current_path = os.path.expanduser("~")
        
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
            self._current_path = os.path.dirname(file_path)
            try:
                self._map_importer.load_map(file_path)
                msg = t("main_window.status_map_loaded", 
                        name=os.path.basename(file_path))
                self._view.show_status_message(msg)
                
            except Exception as e:
                msg = t("dialog.error.generic_load", error=str(e))
                self._view.show_error_message(t("dialog.error.title"), msg)

    @Slot()
    def _on_add_source(self):
        """
        Chamado pelo sinal 'add_source_requested' da View.
        (Modificado para perguntar Global/Local)
        """
        t = self._i18n.t
        
        folder_path = QFileDialog.getExistingDirectory(
            self._view,
            t("dialog.add_source.title"),
            self._current_path
        )
        
        if not folder_path:
            return
            
        self._current_path = folder_path
        
        msg_box = QMessageBox(self._view)
        msg_box.setWindowTitle(t("dialog.add_source.type_title"))
        msg_box.setText(t("dialog.add_source.type_text", name=os.path.basename(folder_path)))
        
        global_button = msg_box.addButton(t("dialog.add_source.type_global"), QMessageBox.YesRole)
        local_button = msg_box.addButton(t("dialog.add_source.type_local"), QMessageBox.NoRole)
        msg_box.addButton(QMessageBox.Cancel)
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        
        # --- CORREÇÃO PRINCIPAL AQUI ---
        # Envia a string em MAIÚSCULAS, que é o que o Enum 'AssociationType'
        # espera.
        if clicked_button == global_button:
            assoc_type = "GLOBAL"
        elif clicked_button == local_button:
            assoc_type = "LOCAL"
        else:
            return # Utilizador cancelou
        # --- FIM DA CORREÇÃO ---

        try:
            self._data_importer.add_data_source(folder_path, assoc_type)
            
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
            self._current_path = os.path.dirname(file_path)
            try:
                self._persistence.save_configuration(file_path)
                msg = t("main_window.status_config_saved", 
                        name=os.path.basename(file_path))
                self._view.show_status_message(msg)
                
            except Exception as e:
                msg = t("dialog.error.generic_save", error=str(e))
                self._view.show_error_message(t("dialog.error.title"), msg)