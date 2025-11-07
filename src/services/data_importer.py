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
#    Data Importer (Service). Analyzes data source folders (Model logic).
#    It is completely independent of Qt/UI.

import os
import glob
import pandas as pd
from typing import Dict, Any, List

class DataImporter:
    """
    Service class responsible for analyzing data source folders.
    
    It finds a sample file (CSV, JSON, Excel) and validates it
    by reading the first few rows to extract column headers.
    """
    
    SUPPORTED_TYPES = {
        "*.csv": "csv",
        "*.json": "json",
        "*.xlsx": "excel",
        "*.xls": "excel"
    }
    
    SAMPLE_ROWS = 5 # Number of rows to read for analysis

    def __init__(self):
        pass

    def analyze_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Analyzes a folder to find a valid sample data file.
        
        Args:
            folder_path (str): The absolute path to the data source folder.
            
        Returns:
            Dict[str, Any]: A dictionary containing 'file_type', 'sample_file',
                            'columns', and 'sample_data'.
                            
        Raises:
            Exception: If no valid files are found or pandas fails to read.
        """
        print(f"DataImporter: Analyzing {folder_path}...")
        
        sample_file_path = None
        file_type = None

        # 1. Find the first supported file
        for pattern, type_id in self.SUPPORTED_TYPES.items():
            search_path = os.path.join(folder_path, pattern)
            files = glob.glob(search_path)
            if files:
                sample_file_path = files[0] # Grab the first match
                file_type = type_id
                break
        
        if not sample_file_path:
            raise Exception(f"No supported data files (.csv, .json, .xlsx, .xls) found in folder.")

        print(f"DataImporter: Found sample file {sample_file_path} (type: {file_type}).")

        # 2. Read the sample file using Pandas
        try:
            df = self._read_sample(sample_file_path, file_type)
            
            columns = list(df.columns)
            sample_data = df.to_dict(orient='records')
            
            print(f"DataImporter: Analysis complete. Columns: {columns}")
            
            return {
                "file_type": file_type,
                "sample_file": os.path.basename(sample_file_path),
                "columns": columns,
                "sample_data": sample_data
            }
            
        except Exception as e:
            print(f"CRITICAL: Pandas failed to read {sample_file_path}. {e}")
            raise Exception(f"File is invalid or corrupt: {e}")

    def _read_sample(self, file_path: str, file_type: str) -> pd.DataFrame:
        """
        Internal helper to read the first N rows of a file using pandas.
        """
        if file_type == "csv":
            return pd.read_csv(file_path, nrows=self.SAMPLE_ROWS)
        elif file_type == "excel":
            return pd.read_excel(file_path, nrows=self.SAMPLE_ROWS)
        elif file_type == "json":
            # read_json doesn't support 'nrows' directly for all orientations.
            # We must read the whole file if it's a record array.
            # For simplicity in this tool, we assume 'orient=records'
            # and just read the first N lines if it's line-delimited.
            try:
                # Try line-delimited JSON
                return pd.read_json(file_path, lines=True, nrows=self.SAMPLE_ROWS)
            except ValueError:
                # Try regular JSON array
                df = pd.read_json(file_path)
                return df.head(self.SAMPLE_ROWS)
        else:
            raise Exception(f"Unsupported file type '{file_type}' for reading.")