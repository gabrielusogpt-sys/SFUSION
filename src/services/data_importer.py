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

# File: src/services/data_importer.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Service class (Model) responsible for analyzing data source files
#    (CSV, JSON, Excel) using Pandas. This service is used to validate
#    data sources and extract metadata (e.g., columns).

import os
from pathlib import Path
from typing import Optional, Dict, List, Any
import pandas as pd

class DataImporter:
    """
    Analyzes data source folders using Pandas.
    
    This service scans a folder for a sample file, attempts to read it,
    and returns metadata about its structure (e.g., file type, columns).
    It does not read the entire dataset.
    """

    # Supported file extensions, mapped to their 'type' (and pandas reader)
    SUPPORTED_EXTENSIONS = {
        ".csv": "csv",
        ".json": "json",
        ".xlsx": "excel",
        ".xls": "excel",
    }

    def __init__(self):
        """
        Initializes the DataImporter.
        """
        print("DataImporter: Initialized.")

    def analyze_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Analyzes a folder, finds a sample file, and reads its header.
        
        Args:
            folder_path (str): The absolute path to the data source folder.
            
        Returns:
            Dict[str, Any]: A dictionary containing metadata, e.g.,
                            {
                                "sample_file": "path/to/sample.csv",
                                "file_type": "csv",
                                "columns": ["col1", "col2", "col3"]
                            }
            
        Raises:
            FileNotFoundError: If the folder is empty or contains no supported files.
            pd.errors.ParserError: If the sample file is malformed.
            Exception: For other unexpected errors.
        """
        print(f"DataImporter: Analyzing folder: {folder_path}")
        
        sample_file_path, file_type = self._find_sample_file(folder_path)
        
        if not sample_file_path:
            raise FileNotFoundError(f"No supported data files (.csv, .json, .xlsx, .xls) found in {folder_path}")

        print(f"DataImporter: Found sample file: {sample_file_path} (Type: {file_type})")

        try:
            # Read only the first 5 rows to get the header
            if file_type == "csv":
                df = pd.read_csv(sample_file_path, nrows=5)
            elif file_type == "json":
                # Try to read as lines=True, common for log data
                try:
                    df = pd.read_json(sample_file_path, lines=True, nrows=5)
                except ValueError:
                    # Fallback to standard JSON
                    df = pd.read_json(sample_file_path, nrows=5)
            elif file_type == "excel":
                df = pd.read_excel(sample_file_path, nrows=5)
            else:
                # This should not be reachable due to _find_sample_file check
                raise ValueError(f"Internal error: Unsupported file type '{file_type}'")

            if df.empty:
                raise ValueError(f"Sample file '{sample_file_path}' is empty.")

            columns = list(df.columns)
            print(f"DataImporter: Analysis successful. Columns found: {columns}")
            
            return {
                "sample_file": str(sample_file_path),
                "file_type": file_type,
                "columns": columns,
            }
            
        except pd.errors.ParserError as e:
            print(f"DataImporter: Error! Pandas could not parse file: {e}")
            raise Exception(f"Failed to parse sample file: {e}")
        except FileNotFoundError as e:
            print(f"DataImporter: Error! File not found: {e}")
            raise  # Re-raise
        except Exception as e:
            print(f"DataImporter: Error! An unexpected error occurred reading file: {e}")
            raise Exception(f"An error occurred reading {sample_file_path}: {e}")

    def _find_sample_file(self, folder_path: str) -> Optional[tuple[Path, str]]:
        """
        Scans a directory and returns the path to the *first*
        supported data file it finds.
        """
        try:
            for entry in os.scandir(folder_path):
                if entry.is_file():
                    ext = Path(entry.name).suffix.lower()
                    if ext in self.SUPPORTED_EXTENSIONS:
                        file_type = self.SUPPORTED_EXTENSIONS[ext]
                        return Path(entry.path), file_type
            return None, None
        except FileNotFoundError:
            return None, None