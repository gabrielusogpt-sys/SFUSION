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

# File: src/utils/i18n.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    Utility class (Model/Service) responsible for loading and managing
#    internationalization (i18n) translation files from .json sources.

import json
import os
from typing import Dict, Any

class I18nManager:
    """
    Manages loading and retrieving translated strings from JSON files.
    """

    def __init__(self, locale_dir: str):
        """
        Initializes the translation manager.

        Args:
            locale_dir (str): The path to the directory containing
                              the locale .json files (e.g., "locale/").
        """
        if not os.path.isdir(locale_dir):
            raise FileNotFoundError(f"Locale directory not found: {locale_dir}")
        self.locale_dir = locale_dir
        self.translations: Dict[str, Any] = {}
        print(f"I18nManager: Initialized for directory: {self.locale_dir}")

    def load_language(self, lang_code: str = "en"):
        """
        Loads a language file (e.g., "pt_BR.json") into memory.

        Args:
            lang_code (str): The language code to load (e.g., "en", "pt_BR").

        Raises:
            FileNotFoundError: If the specified language file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        file_path = os.path.join(self.locale_dir, f"{lang_code}.json")
        
        if not os.path.isfile(file_path):
            print(f"Error: Language file not found: {file_path}")
            raise FileNotFoundError(f"Language file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            print(f"I18nManager: Successfully loaded language '{lang_code}' from {file_path}.")
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON from {file_path}: {e}")
            self.translations = {} # Reset to empty on failure
            raise # Re-raise for the controller to catch
        except Exception as e:
            print(f"Error: An unexpected error occurred loading {file_path}: {e}")
            self.translations = {}
            raise

    def translate(self, key: str) -> str:
        """
        Gets a translated string for a given key.

        Args:
            key (str): The key to translate (e.g., "window_title").

        Returns:
            str: The translated string, or a fallback string if the key
                 is not found in the loaded dictionary.
        """
        if not self.translations:
            print("Warning: Attempted to translate, but no translations are loaded.")
            return f"KEY_ERROR:{key}"
            
        # Access nested keys (e.g., "toolbar.open_map")
        try:
            value = self.translations
            for k in key.split('.'):
                if not isinstance(value, dict):
                    raise KeyError
                value = value[k]
            
            if isinstance(value, str):
                return value
            else:
                # The key exists but its value is not a string (e.g., it's a dict)
                print(f"Warning: Key '{key}' does not map to a final string value.")
                return f"KEY_IS_DICT:{key}"
                
        except KeyError:
            print(f"Warning: Translation key not found: '{key}'")
            return f"KEY_NOT_FOUND:{key}"

    def t(self, key: str) -> str:
        """
        A short alias for the translate() method.
        """
        return self.translate(key)