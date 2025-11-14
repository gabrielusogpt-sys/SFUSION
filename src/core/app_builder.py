import logging
from PySide6.QtWidgets import QMainWindow

# Camada de Modelo e Serviços
from src.domain.app_state import AppState
from src.services.map_importer import MapImporter
from src.services.data_importer import DataImporter
from src.services.persistence import PersistenceService
# Camada de Utilitários
from src.utils.config import ConfigManager
from src.utils.i18n import I18nManager
# Camada de View (UI)
from ui.main_window import MainWindow
from ui.map.map_view import MapView
from ui.sources.sources_panel import SourcesPanel
from ui.editor.editor_panel import EditorPanel
# Camada de Core/Refatoração
from src.core.map_renderer import MapRenderer
# Camada de Controladores
from src.main_controller import MainController
from src.controllers.map_controller import MapController
from src.controllers.sources_controller import SourcesController
from src.controllers.info_controller import InfoController


class AppBuilder:
    """
    Responsabilidade única: Construir e injetar todas as dependências
    da aplicação (Padrão Builder / Injeção de Dependência).
    """

    def __init__(self):
        # Componentes serão armazenados aqui
        self.config = None
        self.i18n = None
        self.app_state = None
        self.map_importer = None
        self.data_importer = None
        self.persistence_service = None
        self.main_window = None
        self.map_view = None
        self.sources_panel = None
        self.editor_panel = None
        self.map_renderer = None
        self.main_controller = None
        self.map_controller = None
        self.sources_controller = None
        self.info_controller = None

    def build(self) -> QMainWindow:
        """Constrói todos os componentes e os conecta."""
        # 1. Utilitários
        self._build_utils()

        # 2. Camada de Modelo e Serviços (Domínio)
        self._build_models()
        self._build_services()

        # 3. Camada de View (UI)
        self._build_views()

        # 4. Camada de Suporte (Core/Renderers)
        self._build_renderers()

        # 5. Camada de Controladores
        self._build_controllers()

        # 6. Conexões finais
        self._setup_connections()

        self.main_window.set_editor_panel(self.editor_panel) 
        self.main_window.set_map_view(self.map_view)
        self.main_window.set_sources_panel(self.sources_panel)

        return self.main_window

    def _build_utils(self):
        self.config = ConfigManager("config/settings.json")
        self.config.load_config() 

        locale_path = self.config.get("locale_path")
        language = self.config.get("language")

        if not locale_path or not language:
            logging.critical("Erro Crítico de Configuração!")
            config_path = self.config.config_path 
            logging.critical(f"  Ficheiro: {config_path}")
            logging.critical("  As chaves 'locale_path' e 'language' estão em falta ou são nulas.")
            logging.critical("  Por favor, verifique o seu 'config/settings.json'.")
            raise ValueError(
                f"Configuração 'locale_path' ou 'language' não encontrada em {config_path}"
            )
        
        self.i18n = I18nManager(locale_path, language) 

    def _build_models(self):
        self.app_state = AppState()

    def _build_services(self):
        self.map_importer = MapImporter(self.app_state)
        self.data_importer = DataImporter(self.app_state)
        self.persistence_service = PersistenceService(self.app_state)

    def _build_views(self):
        self.main_window = MainWindow(self.i18n)
        self.map_view = MapView(self.main_window)
        self.sources_panel = SourcesPanel(self.i18n, self.main_window)
        self.editor_panel = EditorPanel(self.i18n, self.main_window) 

    def _build_renderers(self):
        self.map_renderer = MapRenderer(self.map_view, self.app_state, self.config)

    def _build_controllers(self):
        
        # --- ALTERAÇÃO PRINCIPAL AQUI ---
        # O InfoController agora precisa de 4 argumentos:
        # (Modelo, View, Pintor, Tradutor)
        self.info_controller = InfoController(
            self.app_state, 
            self.editor_panel,
            self.map_renderer, # <-- 1. Nova dependência injetada
            self.i18n
        )
        # --- FIM DA ALTERAÇÃO ---

        self.map_controller = MapController(
            self.app_state, 
            self.map_renderer,
            self.info_controller
        )

        self.main_controller = MainController(
            self.main_window,
            self.map_importer,
            self.data_importer,
            self.persistence_service,
            self.i18n
        )

        self.sources_controller = SourcesController(
            self.app_state, 
            self.sources_panel, 
            self.i18n
        )

    def _setup_connections(self):
        """Conecta todos os sinais e slots."""
        self.main_controller.setup_connections()
        self.map_controller.setup_connections(self.map_view)
        self.sources_controller.setup_connections()
        self.info_controller.setup_connections()