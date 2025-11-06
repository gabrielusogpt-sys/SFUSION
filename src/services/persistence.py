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

# File: src/services/persistence.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Service class (Model) responsible for saving the application state
#    (the mapping configuration) to a SQLite (.db) database file.

import sqlite3
from typing import List, Optional

# Import domain entities
from src.domain.entities import DataSource, MapData, SourceType, ElementType

class PersistenceService:
    """
    Saves and loads mapping configurations to/from a SQLite database.
    
    This is a "worker" service. It is called by a controller,
    it performs a task (file I/O), and returns. It holds no state.
    """
    
    def __init__(self):
        """
        Initializes the PersistenceService.
        """
        print("PersistenceService: Initialized.")

    def save_mapping(self, 
                     save_path: str, 
                     map_base_path: str, 
                     data_sources: List[DataSource]):
        """
        Saves the entire mapping configuration to a SQLite .db file.
        This operation overwrites any existing file at save_path.
        
        Args:
            save_path (str): The absolute path to save the .db file.
            map_base_path (str): The path to the .net.xml file being used.
            data_sources (List[DataSource]): The list of configured data sources.
            
        Raises:
            sqlite3.Error: If any database error occurs.
            Exception: For other unexpected errors.
        """
        print(f"PersistenceService: Attempting to save mapping to {save_path}...")
        
        try:
            # Connect (this creates the file if it doesn't exist)
            with sqlite3.connect(save_path) as conn:
                cursor = conn.cursor()
                
                # Use a transaction for an atomic save
                cursor.execute("BEGIN TRANSACTION")
                
                # 1. (Re)Create the database schema
                self._create_tables(cursor)
                
                # 2. Save the general config (map path)
                self._save_config(cursor, map_base_path)
                
                # 3. Save all data sources
                self._save_data_sources(cursor, data_sources)
                
                # 4. Commit the transaction
                conn.commit()
                
            print(f"PersistenceService: Mapping successfully saved to {save_path}.")
            
        except sqlite3.Error as e:
            print(f"PersistenceService: SQLite Error! {e}. Rolling back.")
            # The 'with' statement handles rollback automatically if commit() isn't reached
            raise Exception(f"Failed to save to database: {e}")
        except Exception as e:
            print(f"PersistenceService: An unexpected error occurred during save: {e}")
            raise

    def _create_tables(self, cursor: sqlite3.Cursor):
        """
        (Re)creates the database schema.
        This drops existing tables to ensure a fresh save.
        """
        cursor.execute("DROP TABLE IF EXISTS MapeamentoFontes")
        cursor.execute("DROP TABLE IF EXISTS ConfiguracaoGeral")
        
        # Table for general key-value config
        cursor.execute("""
            CREATE TABLE ConfiguracaoGeral (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Main table for all source mappings
        cursor.execute("""
            CREATE TABLE MapeamentoFontes (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                parser_id TEXT,
                element_id TEXT,
                element_type TEXT,
                CHECK (source_type IN ('GLOBAL', 'LOCAL'))
            )
        """)

    def _save_config(self, cursor: sqlite3.Cursor, map_base_path: str):
        """ Saves the general configuration data. """
        cursor.execute(
            "INSERT INTO ConfiguracaoGeral (key, value) VALUES (?, ?)",
            ("map_base_path", map_base_path)
        )

    def _save_data_sources(self, cursor: sqlite3.Cursor, data_sources: List[DataSource]):
        """ Saves all data source objects to the MapeamentoFontes table. """
        
        rows_to_insert = []
        
        for source in data_sources:
            element_id: Optional[str] = None
            element_type: Optional[str] = None
            
            # If it's local and has an association, extract its details
            if source.is_local and source.association:
                element_id = source.association.element_id
                element_type = source.association.element_type.name # "NODE" or "EDGE"
            
            # Prepare the data tuple for insertion
            data_tuple = (
                source.id,
                source.path,
                source.source_type.name, # "GLOBAL" or "LOCAL"
                source.parser_id,
                element_id,
                element_type
            )
            rows_to_insert.append(data_tuple)
            
        # Insert all rows at once using executemany for efficiency
        if rows_to_insert:
            cursor.executemany("""
                INSERT INTO MapeamentoFontes 
                (id, path, source_type, parser_id, element_id, element_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, rows_to_insert)