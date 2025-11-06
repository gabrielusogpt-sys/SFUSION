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

# File: src/utils/config.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Utility class (Model/Service) responsible for loading and providing
#    access to application settings from a .json configuration file.

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Manages loading and retrieving application settings from a JSON file.
    """

    def __init__(self, config_path: str):
        """
        Initializes the configuration manager.

        Args:
            config_path (str): The path to the settings.json file.
        """
        if not os.path.isfile(config_path):
            print(f"Warning: Config file not found at {config_path}. Using default values.")
            self.config_path = None
            self.config: Dict[str, Any] = {}
        else:
            self.config_path = config_path
            self.config = {}
            print(f"ConfigManager: Initialized for file: {self.config_path}")

    def load_config(self):
        """
        Loads (or re-loads) the configuration file from disk.
        If the file is missing or corrupt, the config remains empty.
        """
        if not self.config_path:
            return # No config file was found during init

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            print(f"ConfigManager: Successfully loaded settings from {self.config_path}.")
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON from config file {self.config_path}: {e}")
            self.config = {} # Reset to empty on failure
        except FileNotFoundError:
            print(f"Error: Config file {self.config_path} disappeared.")
            self.config = {} # Reset to empty on failure
        except Exception as e:
            print(f"Error: An unexpected error occurred loading config: {e}")
            self.config = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Gets a configuration value for a given key.

        Args:
            key (str): The key to retrieve (e.g., "default_language").
            default (Optional[Any]): The value to return if the key
                                     is not found. Defaults to None.

        Returns:
            Any: The configuration value, or the default value.
        """
        # We can add logic for nested keys (e.g., "database.host") later
        # For now, we assume a flat structure.
        return self.config.get(key, default)