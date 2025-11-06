# SFusion Mapper

[![Status da Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Noxfort-Labs/sfusion)
[![Licença](https://img.shields.io/badge/License-AGPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Uma ferramenta gráfica (GUI) de utilidade, parte do ecossistema SYNAPSE/SFusion, projetada para criar arquivos de configuração de mapeamento de dados.

## 1. Visão Geral e Propósito

O motor ETL principal do **SFusion** é responsável por processar milhões de arquivos de dados históricos (laços indutivos, câmeras, logs de sensores, dados Waze/TomTom) e "fundi-los" em um único dataset coeso.

No entanto, o motor ETL não sabe, por si só, a qual parte da rede de tráfego (mapa) um determinado arquivo de dados pertence.

O **SFusion Mapper** é a ferramenta visual de "Dia Zero" usada pela equipe de implantação da Noxfort Labs para resolver exatamente este problema. Sua única função é permitir que um engenheiro:

1.  Carregue um mapa de topologia de tráfego (ex: `sumo.net.xml`).
2.  Carregue as pastas de fontes de dados brutos (ex: `camera_logs/`).
3.  Associe visualmente os dados "Locais" (câmeras, laços) a elementos específicos do mapa (nós ou arestas) **clicando** neles.
4.  Gere um arquivo de banco de dados (`.db` SQLite) que serve como o **arquivo de configuração** para o motor ETL principal.

Este programa *não* processa os dados. Ele *apenas* cria o "mapa de instruções" que o motor ETL usará.

## 2. Funcionalidades Principais

* **Renderização de Mapa:** Carrega e exibe mapas de topologia `.net.xml` do SUMO usando a biblioteca PySide6 (Qt).
* **Interação de Mapa:** Permite zoom e pan (arrastar) para navegação fácil em redes de cidades complexas.
* **Gerenciamento de Fontes:** Permite adicionar múltiplas pastas de fontes de dados.
* **Classificação de Dados:** Permite classificar fontes como:
    * **Global:** Dados que se aplicam à rede inteira (ex: Waze, TomTom).
    * **Local:** Dados que vêm de um sensor físico específico (ex: câmera, laço indutivo).
* **Mapeamento Visual:** Para fontes "Locais", o usuário pode clicar diretamente em um nó (cruzamento) ou aresta (rua) no mapa para criar a associação.
* **Saída SQLite:** Gera um banco de dados `mapeamento.db` que armazena todas essas associações de forma estruturada.
* **Internacionalização (i18n):** Suporte a múltiplos idiomas (PT-BR, EN, ES, etc.) carregados dinamicamente de arquivos `locale/*.json`.

## 3. Arquitetura Técnica

O projeto utiliza **Python** e a biblioteca **PySide6 (Qt6)** para a interface gráfica.

Ele segue uma arquitetura **Model-View-Controller (MVC)** estrita para garantir uma separação clara de responsabilidades (SRP) e facilitar a manutenção e os testes.

* **`sfusion.py`:** O ponto de entrada (lançador) que inicializa e conecta as camadas.
* **`ui/` (View):** A camada de apresentação, responsável *apenas* pela aparência. É "burra" e apenas emite sinais (ex: "botão clicado").
    * `ui/main_window/`: O "shell" principal da aplicação.
    * `ui/map/`: O componente visual do mapa (`QGraphicsView`).
    * `ui/sources/`: O componente de lista de fontes de dados.
* **`src/` (Model & Controller):** A camada de lógica, dividida em:
    * **`src/controllers/` (Controller):** A "cola" que ouve os sinais da `ui/`, toma decisões e coordena as ações.
    * **`src/domain/` (Model):** Define as estruturas de dados (ex: `Node`, `Edge`) e o estado da aplicação.
    * **`src/services/` (Model):** Lida com "trabalho", como analisar (parse) o `.net.xml` (`map_importer.py`) e salvar o banco de dados (`persistence.py`).
    * **`src/utils/` (Model):** Ferramentas de suporte, como o tradutor (`i18n.py`).

## 4. Fluxo de Trabalho do Usuário

1.  O engenheiro de implantação executa `python sfusion.py`.
2.  A janela principal é aberta.
3.  O engenheiro clica em "Abrir Mapa" e seleciona o arquivo `sumo.net.xml` da cidade. O mapa é renderizado no painel principal.
4.  O engenheiro clica em "Adicionar Fonte" e seleciona uma pasta (ex: `/dados/cameras_centro/`).
5.  A pasta aparece no painel de "Fontes de Dados". O engenheiro a seleciona e a define como "Local".
6.  O programa pede uma associação. O engenheiro clica no cruzamento `J10` correspondente no mapa.
7.  A associação é criada. O engenheiro repete o processo para uma fonte "Global" (ex: `/dados/waze/`), que não requer um clique no mapa.
8.  Ao final, o engenheiro clica em "Salvar Mapeamento".
9.  O programa gera o arquivo `mapeamento.db`. Este arquivo é então entregue ao motor ETL principal do SFusion.

## 5. Como Executar (Ambiente de Desenvolvimento)

```bash
# 1. Clone o repositório
git clone [https://github.com/Noxfort-Labs/sfusion.git](https://github.com/Noxfort-Labs/sfusion.git)
cd sfusion

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
# (As dependências serão listadas em pyproject.toml)
pip install pyside6 lxml

# 4. Execute o programa
python3 sfusion.py