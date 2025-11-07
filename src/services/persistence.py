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
#    Persistence Service (Service). Saves the mapping to a .db (Model logic).
#    It is completely independent of Qt/UI.

import sqlite3
import os
from typing import List, Iterable

# FIX: Changed import to be absolute from the project root (src.)
from src.domain.entities import DataSource, AssociationType
# --- END FIX ---


class PersistenceService:
    """
    Service class responsible for saving the final mapping configuration
    to an SQLite (.db) database file.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        pass

    def save_mapping(self, 
                     save_path: str, 
                     map_base_path: str, 
                     data_sources: Iterable[DataSource]):
        """
        Creates or overwrites a .db file with the current mapping config.
        
        Args:
            save_path (str): The absolute path to the .db file to create.
            map_base_path (str): The absolute path to the .net.xml file used.
            data_sources (Iterable[DataSource]): A list of all DataSource entities.
            
        Raises:
            Exception: If sqlite3 fails to write to the database.
        """
        print(f"PersistenceService: Saving mapping to {save_path}...")
        
        # Ensure directory exists (though QFileDialog usually handles this)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Delete the file if it already exists to ensure a fresh start
        if os.path.exists(save_path):
            os.remove(save_path)
            
        try:
            # Connect (this will create the file)
            with sqlite3.connect(save_path) as conn:
                cursor = conn.cursor()
                
                # --- 1. Create ConfiguracaoGeral Table ---
                # Stores the path to the map this config was based on
                cursor.execute("""
                CREATE TABLE ConfiguracaoGeral (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL
                )
                """)
                
                # --- 2. Create MapeamentoFontes Table ---
                # Stores the main mapping relationships
                cursor.execute("""
                CREATE TABLE MapeamentoFontes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fonte_id_unico TEXT NOT NULL,
                    caminho_dados TEXT NOT NULL,
                    parser_id TEXT,
                    tipo_associacao TEXT NOT NULL,
                    associacao_local_id TEXT
                )
                """)
                
                conn.commit()
                print("PersistenceService: Tables created successfully.")

                # --- 3. Insert General Config Data ---
                map_filename = os.path.basename(map_base_path)
                cursor.execute(
                    "INSERT INTO ConfiguracaoGeral (chave, valor) VALUES (?, ?)",
                    ("map_base_file", map_filename)
                )
                
                # --- 4. Insert Data Source Mappings ---
                rows_to_insert = []
                for source in data_sources:
                    rows_to_insert.append((
                        source.id,
                        source.path,
                        source.parser_id,
                        source.association_type.value, # "GLOBAL" or "LOCAL"
                        source.associated_node_id # Will be NULL if not applicable
                    ))
                
                cursor.executemany("""
                INSERT INTO MapeamentoFontes 
                    (fonte_id_unico, caminho_dados, parser_id, tipo_associacao, associacao_local_id)
                VALUES (?, ?, ?, ?, ?)
                """, rows_to_insert)

                conn.commit()
                
                print(f"PersistenceService: Save complete. {len(rows_to_insert)} sources saved.")

        except sqlite3.Error as e:
            print(f"CRITICAL: SQLite error during save: {e}")
            # Clean up the (likely corrupt) file
            if os.path.exists(save_path):
                os.remove(save_path)
            raise Exception(f"Database error: {e}")
        except Exception as e:
            print(f"CRITICAL: Unknown error during save: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            raise Exception(f"Unknown error: {e}")