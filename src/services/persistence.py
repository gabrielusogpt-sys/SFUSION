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

# File: src/services/persistence.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    PersistenceService (Service). Saves the configuration map to a .db.

import logging
import sqlite3
import json
from PySide6.QtCore import QObject, Slot, QRunnable, QThreadPool

# 1. Importar o AppState
from src.domain.app_state import AppState


class PersistenceWorker(QRunnable):
    """
    Trabalhador (Worker) para salvar a configuração em .db numa thread separada.
    """
    # 2. Aceitar o app_state
    def __init__(self, file_path: str, app_state: AppState):
        super().__init__()
        self.file_path = file_path
        # 3. Armazenar a referência
        self._app_state = app_state 

    @Slot()
    def run(self):
        """Executa a lógica de salvamento."""
        logging.info(f"PersistenceWorker: Iniciando salvamento em '{self.file_path}'...")
        try:
            # 4. Obter os dados mais recentes do AppState
            nodes = self._app_state.get_all_nodes()
            edges = self._app_state.get_all_edges()
            sources = self._app_state.get_all_data_sources()
            
            self._create_database_and_save(nodes, edges, sources)
            logging.info(f"PersistenceWorker: Configuração salva com sucesso em {self.file_path}")

        except sqlite3.Error as e:
            logging.error(f"PersistenceWorker: Erro de SQLite ao salvar em {self.file_path}: {e}")
        except Exception as e:
            logging.error(f"PersistenceWorker: Falha inesperada ao salvar configuração: {e}", exc_info=True)

    def _create_database_and_save(self, nodes, edges, sources):
        """
        Cria/Substitui o ficheiro .db e insere os dados.
        """
        with sqlite3.connect(self.file_path) as conn:
            cursor = conn.cursor()
            
            # --- Tabela 1: Metadados de Nós (Nós/Interseções) ---
            cursor.execute("DROP TABLE IF EXISTS node_metadata")
            cursor.execute("""
                CREATE TABLE node_metadata (
                    sumo_id TEXT PRIMARY KEY,
                    real_name TEXT
                )
            """)
            # Filtra apenas os nós que o utilizador renomeou
            node_data = [
                (n.id, n.real_name) for n in nodes if n.real_name
            ]
            if node_data:
                cursor.executemany("INSERT INTO node_metadata VALUES (?, ?)", node_data)

            # --- Tabela 2: Metadados de Arestas (Ruas) ---
            cursor.execute("DROP TABLE IF EXISTS edge_metadata")
            cursor.execute("""
                CREATE TABLE edge_metadata (
                    sumo_id TEXT PRIMARY KEY,
                    real_name TEXT
                )
            """)
            # Filtra apenas as arestas que o utilizador renomeou
            edge_data = [
                (e.id, e.real_name) for e in edges if e.real_name
            ]
            if edge_data:
                cursor.executemany("INSERT INTO edge_metadata VALUES (?, ?)", edge_data)
            
            # --- Tabela 3: Associações de Fontes de Dados ---
            cursor.execute("DROP TABLE IF EXISTS data_associations")
            cursor.execute("""
                CREATE TABLE data_associations (
                    source_name TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    association_type TEXT NOT NULL,
                    associated_element_id TEXT,
                    file_types_json TEXT
                )
            """)
            # Salva todas as fontes de dados
            source_data = [
                (
                    s.name, 
                    s.path, 
                    s.association_type, 
                    s.associated_element_id, 
                    json.dumps(s.file_types) # Serializa a lista de tipos
                ) for s in sources
            ]
            if source_data:
                cursor.executemany("INSERT INTO data_associations VALUES (?, ?, ?, ?, ?)", source_data)

            # Confirma as transações
            conn.commit()


class PersistenceService(QObject):
    """
    Serviço de persistência. Gere a pool de threads para salvar
    o AppState num ficheiro .db (SQLite).
    (Refatorado do MainController)
    """
    
    # --- 5. Alteração Principal: Corrigir o __init__ ---
    def __init__(self, app_state: AppState):
        super().__init__()
        # 6. Armazenar a referência
        self._app_state = app_state 
        self._thread_pool = QThreadPool.globalInstance()
        logging.info("PersistenceService (Serviço) inicializado.")

    @Slot(str)
    def save_configuration(self, file_path: str):
        """
        Inicia um PersistenceWorker numa thread separada.
        """
        if not file_path:
            logging.warning("PersistenceService: 'save_configuration' chamado com caminho vazio.")
            return
            
        if not file_path.endswith(".db"):
            file_path += ".db"
            logging.info(f"PersistenceService: Nome do ficheiro corrigido para '{file_path}'")

        # 7. Passar o app_state (que contém os dados) para o Worker
        worker = PersistenceWorker(file_path, self._app_state)
        
        # (Opcional: conectar sinais de conclusão/erro do worker)

        self._thread_pool.start(worker)