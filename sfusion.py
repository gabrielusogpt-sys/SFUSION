#!/usr/bin/env python3
#
# SFusion Mapper - Ferramenta de Configuração ETL "Dia Zero"
# Copyright (C) 2024 Noxfort Labs (https://github.com/noxfort)
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

import sys
import os
import logging
import logging.handlers
from PySide6.QtWidgets import QApplication

# --- Configuração de Caminhos (Paths) ---
# Define o diretório raiz da aplicação (APP_ROOT)
# __file__ é o caminho para este script (sfusion.py)
# os.path.abspath obtém o caminho absoluto
# os.path.dirname obtém o diretório que contém o ficheiro
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Adiciona os diretórios 'src' e 'ui' ao sys.path
# Isto permite que o Python encontre os módulos (ex: from src.core...)
sys.path.append(os.path.join(APP_ROOT, 'src'))
sys.path.append(os.path.join(APP_ROOT, 'ui'))

# --- Importação de Componentes (após configuração do path) ---
from src.core.app_builder import AppBuilder


def setup_logging():
    """Configura o sistema de logging global."""
    
    # Define o formato da mensagem de log
    log_format = (
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] "
        "%(message)s (%(filename)s:%(lineno)d)"
    )
    
    # Nível de log: INFO para ver mensagens gerais, DEBUG para detalhes
    log_level = logging.INFO 

    # Configuração básica de logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)  # Envia logs para o console
        ]
    )
    
    # (Opcional) Configurar log para ficheiro
    # try:
    #     log_file = os.path.join(APP_ROOT, "sfusion_mapper.log")
    #     # Rotaciona o log: 5 ficheiros de 1MB cada
    #     file_handler = logging.handlers.RotatingFileHandler(
    #         log_file, maxBytes=(1024*1024), backupCount=5
    #     )
    #     file_handler.setFormatter(logging.Formatter(log_format))
    #     logging.getLogger().addHandler(file_handler)
    # except PermissionError:
    #     logging.warning(f"Não foi possível escrever em {log_file}. Log em ficheiro desativado.")


def main():
    """Função principal: Inicializa e executa a aplicação."""
    
    # 1. Configura o logging ANTES de qualquer outra coisa
    setup_logging()
    logging.info(f"Iniciando SFusion Mapper... (APP_ROOT: {APP_ROOT})")

    # 2. Cria a aplicação Qt
    app = QApplication(sys.argv)

    # 3. Usa o AppBuilder para construir a aplicação (Nova Lógica)
    # O AppBuilder agora constrói TUDO internamente (Janela, Modelos, Controlo)
    try:
        builder = AppBuilder()
        main_window = builder.build()
        
        # 4. Mostra a janela principal
        main_window.show()
        logging.info("Aplicação iniciada com sucesso.")

        # 5. Executa o loop de eventos da aplicação
        sys.exit(app.exec())

    except Exception as e:
        # Erro fatal durante a inicialização
        logging.critical(f"Falha crítica ao construir a aplicação: {e}", exc_info=True)
        # (Opcional) Mostrar um pop-up de erro
        # QMessageBox.critical(None, "Erro Crítico", f"A aplicação falhou ao iniciar:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()