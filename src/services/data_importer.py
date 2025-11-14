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

# File: src/services/data_importer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    DataImporter (Service). Manages analyzing and adding data sources.

import os
import logging
import pandas as pd
from PySide6.QtCore import QObject, Slot, QRunnable, QThreadPool, Signal

from src.domain.app_state import AppState
from src.domain.entities import DataSource, AssociationType


class DataImportWorker(QRunnable):
    """
    Trabalhador (Worker) para analisar uma pasta de fonte de dados.
    """
    
    # (Corrigido para aceitar assoc_type)
    def __init__(self, folder_path: str, app_state: AppState, assoc_type: str):
        super().__init__()
        self.folder_path = folder_path
        self._app_state = app_state
        self.assoc_type = assoc_type # "GLOBAL" ou "LOCAL" (em maiúsculas)
        self.signals = QObject() 

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

            # --- CORREÇÃO (Revertida para a chamada direta) ---
            # Como o MainController já envia "GLOBAL" ou "LOCAL",
            # podemos passar 'self.assoc_type' diretamente para o Enum.
            try:
                assoc_enum = AssociationType(self.assoc_type)
            except ValueError:
                # Este 'except' agora só deve acontecer se algo correr muito mal
                logging.error(f"DataImportWorker: Tipo de associação desconhecido '{self.assoc_type}'. A usar UNASSOCIATED.")
                assoc_enum = AssociationType.UNASSOCIATED
            # --- FIM DA CORREÇÃO ---

            new_source = DataSource(
                path=self.folder_path,
                name=os.path.basename(self.folder_path),
                file_types=file_types,
                association_type=assoc_enum, # <-- Lógica atualizada
                associated_element_id=None
            )
            
            self._app_state.add_data_source(new_source)
            
            logging.info(f"DataImportWorker: Análise concluída para {self.folder_path}. Tipos: {file_types}")

        except Exception as e:
            logging.error(f"DataImportWorker: Falha ao analisar {self.folder_path}: {e}", exc_info=True)

    def _analyze_folder(self, folder_path):
        """Varre a pasta e retorna os tipos de ficheiros suportados."""
        types = set()
        try:
            for file_name in os.listdir(folder_path):
                file_lower = file_name.lower()
                
                if file_lower.endswith((".csv", ".csv.gz")):
                    types.add("CSV")
                elif file_lower.endswith((".json", ".json.gz")):
                    types.add("JSON")
                elif file_lower.endswith((".xml", ".xml.gz")):
                    if not file_lower.endswith(".net.xml") and not file_lower.endswith(".net.xml.gz"):
                        types.add("XML")
                elif file_lower.endswith((".xls", ".xlsx")):
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
    """
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self._app_state = app_state 
        self._thread_pool = QThreadPool.globalInstance()
        logging.info("DataImporter (Serviço) inicializado.")

    # (Corrigido para aceitar assoc_type)
    @Slot(str, str)
    def add_data_source(self, folder_path: str, assoc_type: str):
        """
        Inicia um DataImportWorker numa thread separada.
        """
        if not folder_path or not os.path.isdir(folder_path):
            logging.warning(f"DataImporter: Caminho de pasta inválido fornecido: '{folder_path}'")
            return

        # (Corrigido para passar assoc_type)
        worker = DataImportWorker(folder_path, self._app_state, assoc_type) 
        self._thread_pool.start(worker)