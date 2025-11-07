# SFusion (SYNAPSE Fusion) Mapper
#
# Copyright (C) 2025 Gabriel Moraes - Noxfort Labs
#
# Este programa é software livre: pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral Affero GNU como publicada pela
# Free Software Foundation, quer a versão 3 da Licença, ou
# (à sua opção) qualquer versão posterior.
#
# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Veja a
# Licença Pública Geral Affero GNU para mais detalhes.
#
# Deveria ter recebido uma cópia da Licença Pública Geral Affero GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

# File: src/controllers/info_controller.py
# Author: Gabriel Moraes
# Date: November 2025
# Description:
#    InfoController (Controller). O "cérebro" para o EditorPanel.
#    (Refatorado para usar o EditorPanel fixo em vez do InfoPanel flutuante)

import logging
from PySide6.QtCore import QObject, Slot

from src.domain.app_state import AppState
from src.domain.entities import MapNode, MapEdge
from src.utils.i18n import I18nManager

# 1. Alterar a importação da View
from ui.editor.editor_panel import EditorPanel


class InfoController(QObject):
    """
    Controlador para o EditorPanel.
    
    Responsabilidade:
    - Ouvir os sinais do EditorPanel (View).
    - Atualizar o AppState (Model) quando 'Salvar' é clicado.
    - Orquestrar a exibição/ocultação do painel (agora fixo à esquerda).
    """
    
    def __init__(
        self,
        app_state: AppState,
        view: EditorPanel,  # 2. Alterar o type hint (de InfoPanel para EditorPanel)
        i18n: I18nManager
    ):
        """
        Inicializa o controlador.
        
        :param app_state: A "Fonte Única da Verdade".
        :param view: A View (EditorPanel) que este controlador gere.
        :param i18n: O gestor de internacionalização.
        """
        super().__init__() 
        
        self._app_state = app_state
        self._view = view
        self._i18n = i18n
        
        self._current_element = None # Armazena o Nó ou Aresta atual

    def setup_connections(self):
        """Conecta os sinais da View aos slots deste controlador."""
        # (Esta lógica é idêntica, pois o EditorPanel emite os mesmos sinais)
        self._view.save_clicked.connect(self._on_save)
        self._view.close_clicked.connect(self.hide_panel)

    # --- Métodos Públicos (Chamados pelo MapController) ---

    @Slot(MapNode)
    def show_for_node(self, node: MapNode):
        """Exibe o painel com os dados de um Nó."""
        self._current_element = node
        t = self._i18n.t
        
        self._view.show_data(
            title=t("info_panel.title_node"), # Título
            sumo_id=node.id,
            real_name=node.real_name
        )
        
        # 3. Adicionar chamada explícita para mostrar o painel
        self._view.show()
        self._view.raise_()

    @Slot(MapEdge)
    def show_for_edge(self, edge: MapEdge):
        """Exibe o painel com os dados de uma Aresta."""
        self._current_element = edge
        t = self._i18n.t
        
        self._view.show_data(
            title=t("info_panel.title_edge"), # Título
            sumo_id=edge.id,
            real_name=edge.real_name
        )
        
        # 3. Adicionar chamada explícita para mostrar o painel
        self._view.show()
        self._view.raise_()

    @Slot()
    def hide_panel(self):
        """Esconde o painel e limpa o elemento atual."""
        self._current_element = None
        self._view.hide()

    # --- Slots Privados (Ouvem a View) ---

    @Slot(str)
    def _on_save(self, new_real_name: str):
        """
        Chamado quando o botão 'Salvar' na View é clicado.
        Atualiza o Modelo (AppState).
        """
        if self._current_element:
            logging.info(f"InfoController: Salvando '{new_real_name}' para o ID {self._current_element.id}")
            
            # Atualiza o modelo (AppState)
            self._app_state.update_element_real_name(
                self._current_element.id, 
                new_real_name
            )
            
            # (Opcional: Adicionar feedback na status bar)
            
            # Esconde o painel após salvar
            self.hide_panel()
        
        else:
            logging.warning("InfoController: 'Salvar' clicado, mas nenhum elemento estava selecionado.")