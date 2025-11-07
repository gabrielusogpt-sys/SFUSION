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

# File: src/utils/i18n.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    I18nManager (Utility). Loads and manages translation .json files.

import json
import os

class I18nManager:
    """
    Manages loading and accessing translations from .json files.
    """
    def __init__(self, locale_dir: str):
        """
        Initializes the manager with the path to the locale directory.
        
        Args:
            locale_dir (str): The absolute path to the 'locale'
                              or 'locale_backend' directory.
        """
        self.locale_dir = locale_dir
        self._translations = {}
        print(f"I18nManager: Initialized for directory: {self.locale_dir}")

    def load_language(self, language_code: str):
        """
        Loads a specific language file (e.g., "pt_BR.json") from the
        locale directory into memory.
        
        Args:
            language_code (str): The language code (e.g., "pt_BR", "en").
            
        Raises:
            Exception: Propagates exceptions if file loading fails critically.
        """
        lang_file_path = os.path.join(self.locale_dir, f"{language_code}.json")
        
        if not os.path.exists(lang_file_path):
            print(f"Warning: Language file not found at {lang_file_path}. Using empty.")
            self._translations = {}
            return

        try:
            with open(lang_file_path, 'r', encoding='utf-8') as f:
                self._translations = json.load(f)
            print(f"I18nManager: Successfully loaded language '{language_code}' from {lang_file_path}.")
            
        except json.JSONDecodeError as e:
            # FIX: Added robust error logging
            print(f"CRITICAL: Failed to parse {lang_file_path}: {e}. Using empty.")
            self._translations = {}
            raise e # Re-raise to stop execution if translations fail
        except Exception as e:
            # FIX: Added robust error logging
            print(f"CRITICAL: Failed to read {lang_file_path}: {e}. Using empty.")
            self._translations = {}
            raise e # Re-raise to stop execution
            # --- END FIX ---

    def t(self, key: str, default: str = None) -> str:
        """
        Translates a given key.
        
        Args:
            key (str): The key to translate (e.g., "main_window.title").
            default (str, optional): A fallback value if the key is not found.
        
        Returns:
            str: The translated string, the default, or a warning message.
        """
        # --- FIX ---
        # The JSON files use flat keys (e.g., "main_window.window_title")
        # not nested keys. The original code (which split the key by '.')
        # was incorrect for the JSON file structure.
        #
        # We must look up the entire key string directly.
        try:
            return self._translations[key]
        
        # --- END FIX ---
        except KeyError:
            print(f"Warning: Translation key not found: '{key}'")
            if default:
                return default
            return f"KEY_NOT_FOUND: {key}"
        except Exception as e:
            print(f"Error during translation of key '{key}': {e}")
            return f"ERROR: {key}"