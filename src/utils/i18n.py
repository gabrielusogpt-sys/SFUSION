import json
import os
import logging

class I18nManager:
    """
    Gestor de Internacionalização (i18n).
    Lê ficheiros .json de tradução.
    """
    
    # 1. Alterar o __init__ para aceitar 'default_lang'
    def __init__(self, locale_path: str = "locale", default_lang: str = "en"):
        """
        Inicializa o gestor.
        :param locale_path: Caminho para a pasta 'locale' (ex: "locale")
        :param default_lang: Língua a ser carregada (ex: "en", "pt_BR")
        """
        self.locale_path = locale_path
        self.translations = {}
        
        # 2. Usar o 'default_lang' em vez de "en" hardcoded
        try:
            self.set_language(default_lang)
        except FileNotFoundError:
            # Fallback: Se a língua pedida não existir, tenta carregar 'en'
            logging.error(f"Ficheiro de tradução '{default_lang}.json' não encontrado.")
            logging.warning("A carregar 'en' (Inglês) como fallback.")
            try:
                self.set_language("en")
            except FileNotFoundError:
                # Se nem 'en' existir, a UI ficará sem texto.
                logging.critical("Ficheiro 'en.json' de fallback não encontrado. A UI pode estar vazia.")
                # self.translations continua a ser {}

    def set_language(self, lang_code: str):
        """Carrega um ficheiro de língua (ex: "pt_BR") da pasta locale."""
        file_path = os.path.join(self.locale_path, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            # Lança um erro claro se o ficheiro não for encontrado
            raise FileNotFoundError(f"Ficheiro de tradução não encontrado: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            logging.info(f"Traduções carregadas de: {file_path}")
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao ler o JSON de tradução {file_path}: {e}")
            self.translations = {} # Garante que não usamos traduções corruptas
        except Exception as e:
            logging.error(f"Erro desconhecido ao carregar {file_path}: {e}")
            self.translations = {}


    def t(self, key: str, **kwargs) -> str:
        """
        Traduz uma chave (key) usando o dicionário carregado.
        (Corrigido para ler chaves 'planas' ex: "main_window.title")
        """
        try:
            # Acede diretamente à chave
            translation = self.translations.get(key)
            
            # Se a chave não for encontrada, retorna a própria chave
            if translation is None:
                logging.warning(f"Chave de tradução não encontrada: '{key}'")
                return key

            # (Opcional) Substitui placeholders (ex: {nome})
            if kwargs:
                translation = translation.format(**kwargs)
                
            return translation
            
        except KeyError:
            # Isto pode acontecer se a chave existir mas o .format() falhar
            logging.warning(f"Erro de formatação na tradução da chave: '{key}'")
            return key
        except Exception as e:
            logging.error(f"Erro ao traduzir '{key}': {e}")
            return key