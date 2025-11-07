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

# File: src/services/data_importer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    DataImporter (Service). Manages analyzing and adding data sources.

import os
import logging
import pandas as pd
from PySide6.QtCore import QObject, Slot, QRunnable, QThreadPool, Signal

# 1. Importar o AppState e DataSource
from src.domain.app_state import AppState
from src.domain.entities import DataSource


class DataImportWorker(QRunnable):
    """
    Trabalhador (Worker) para analisar uma pasta de fonte de dados.
    """
    
    # 2. Aceitar o app_state
    def __init__(self, folder_path: str, app_state: AppState):
        super().__init__()
        self.folder_path = folder_path
        # 3. Armazenar a referência
        self._app_state = app_state
        self.signals = QObject() # Para emitir sinais se necessário

    @Slot()
    def run(self):
        """
        Analisa a pasta, identifica tipos de ficheiros e atualiza o AppState.
        """
        logging.info(f"DataImportWorker: Analisando '{self.folder_path}'...")
        try:
            file_types = self._analyze_folder(self.folder_path)
            
            if not file_types:
                logging.warning(f"DataImportWorker: Nenhuma fonte de dados válida encontrada em {self.folder_path}")
                return

            # Cria a entidade DataSource
            new_source = DataSource(
                path=self.folder_path,
                name=os.path.basename(self.folder_path),
                file_types=file_types,
                association_type="local", # Padrão
                associated_element_id=None
            )
            
            # 4. Atualiza o AppState (isto emitirá o sinal data_sources_changed)
            self._app_state.add_data_source(new_source)
            
            logging.info(f"DataImportWorker: Análise concluída para {self.folder_path}. Tipos: {file_types}")

        except Exception as e:
            logging.error(f"DataImportWorker: Falha ao analisar {self.folder_path}: {e}", exc_info=True)

    def _analyze_folder(self, folder_path):
        """Varre a pasta e retorna os tipos de ficheiros suportados."""
        types = set()
        try:
            for file_name in os.listdir(folder_path):
                # (Lógica simples de deteção)
                if file_name.endswith((".csv", ".csv.gz")):
                    types.add("CSV")
                elif file_name.endswith((".json", ".json.gz")):
                    types.add("JSON")
                elif file_name.endswith((".xls", ".xlsx")):
                    types.add("Excel")
        except FileNotFoundError:
            logging.error(f"DataImportWorker: Pasta não encontrada: {folder_path}")
            return []
        except NotADirectoryError:
            logging.error(f"DataImportWorker: O caminho não é uma pasta: {folder_path}")
            return []
            
        return list(types)


class DataImporter(QObject):
    """
    Serviço para importar fontes de dados. Gere a pool de threads.
    (Refatorado do MainController)
    """
    
    # --- 5. Alteração Principal: Corrigir o __init__ ---
    def __init__(self, app_state: AppState):
        super().__init__()
        # 6. Armazenar a referência
        self._app_state = app_state 
        self._thread_pool = QThreadPool.globalInstance()
        logging.info("DataImporter (Serviço) inicializado.")

    @Slot(str)
    def add_data_source(self, folder_path: str):
        """
        Inicia um DataImportWorker numa thread separada.
        """
        if not folder_path or not os.path.isdir(folder_path):
            logging.warning(f"DataImporter: Caminho de pasta inválido fornecido: '{folder_path}'")
            return

        # 7. Passar o app_state para o Worker
        worker = DataImportWorker(folder_path, self._app_state) 
        
        # (Opcional: conectar sinais de conclusão)

        self._thread_pool.start(worker)