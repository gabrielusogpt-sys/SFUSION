import logging
import gzip
from lxml import etree
from PySide6.QtCore import QObject, Slot, QRunnable, QThreadPool, Signal

from src.domain.app_state import AppState
from src.domain.entities import MapNode, MapEdge

class MapImportWorker(QRunnable):
    """
    Trabalhador (Worker) para importar o mapa numa thread separada
    para não bloquear a UI.
    """
    def __init__(self, file_path: str, app_state: AppState):
        super().__init__()
        self.file_path = file_path
        self._app_state = app_state

    @Slot()
    def run(self):
        """Executa a importação do mapa."""
        logging.info(f"MapImportWorker: Iniciando importação de '{self.file_path}'...")
        try:
            nodes, edges = self._parse_net_xml(self.file_path)
            
            if not nodes and not edges:
                logging.warning(f"MapImportWorker: Ficheiro '{self.file_path}' não continha nós ou arestas.")
            
            self._app_state.set_map_data(nodes, edges)
            
            logging.info(f"MapImportWorker: Importação concluída. {len(nodes)} nós, {len(edges)} arestas.")

        except etree.XMLSyntaxError as e:
            logging.error(f"MapImportWorker: Erro de sintaxe XML ao ler '{self.file_path}': {e}")
        except Exception as e:
            logging.error(f"MapImportWorker: Erro inesperado ao importar mapa: {e}", exc_info=True)

    def _parse_net_xml(self, file_path):
        """Lê o ficheiro .net.xml (ou .net.xml.gz) e extrai dados."""
        
        open_func = gzip.open if file_path.endswith('.gz') else open
        
        with open_func(file_path, 'rb') as f:
            parser = etree.XMLParser(target=NetXMLParserTarget())
            etree.parse(f, parser)
            
            return parser.target.nodes, parser.target.edges


class NetXMLParserTarget(object):
    """
    Alvo (target) do parser lxml. Chamado incrementalmente
    à medida que o XML é lido. (Poupa muita memória)
    """
    def __init__(self):
        self.nodes = []
        self.edges = []
        self._current_edge = None

    def start(self, tag, attrib):
        """Chamado quando uma tag <tag> é aberta."""
        try:
            # (Corrigido para corresponder à entidade MapNode)
            if tag == "junction" and attrib.get("type") != "internal":
                node = MapNode(
                    id=attrib["id"],
                    x=float(attrib["x"]),
                    y=float(attrib["y"]),
                    node_type=attrib.get("type", "unknown"),
                    real_name=None 
                )
                self.nodes.append(node)

            # (Corrigido para corresponder à entidade MapEdge)
            elif tag == "edge" and not attrib.get("function") == "internal":
                self._current_edge = {
                    "id": attrib["id"],
                    "from_node": attrib["from"],
                    "to_node": attrib["to"],
                    "shape": []
                }
            
            elif tag == "lane" and self._current_edge is not None:
                shape_str = attrib.get("shape")
                if shape_str:
                    points = [
                        (float(p.split(',')[0]), float(p.split(',')[1]))
                        for p in shape_str.split(' ')
                    ]
                    # Apenas a primeira "lane" define a geometria
                    if not self._current_edge["shape"]:
                        self._current_edge["shape"] = points

        except KeyError as e:
            logging.warning(f"NetXMLParserTarget: Atributo em falta no XML: {e} (Tag: {tag}, Attrs: {attrib})")
        except Exception as e:
            logging.error(f"NetXMLParserTarget: Erro no 'start' (Tag: {tag}): {e}")


    def end(self, tag):
        """Chamado quando uma tag </tag> é fechada."""
        if tag == "edge" and self._current_edge is not None:
            # (Corrigido para corresponder à entidade MapEdge)
            if self._current_edge["shape"]:
                edge = MapEdge(
                    id=self._current_edge["id"],
                    from_node=self._current_edge["from_node"],
                    to_node=self._current_edge["to_node"],
                    shape=self._current_edge["shape"],
                    real_name=None
                )
                self.edges.append(edge)
            
            self._current_edge = None

    def data(self, data):
        pass

    def close(self):
        return "Parsing finished"


class MapImporter(QObject):
    """
    Serviço de importação de mapa. Gere a pool de threads.
    (Esta é a classe que estava em falta)
    """
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self._app_state = app_state
        self._thread_pool = QThreadPool.globalInstance()
        logging.info("MapImporter (Serviço) inicializado.")

    @Slot(str)
    def load_map(self, file_path: str):
        """
        Inicia um MapImportWorker numa thread separada para carregar o mapa.
        """
        if not file_path:
            logging.warning("MapImporter: 'load_map' chamado com caminho vazio.")
            return

        worker = MapImportWorker(file_path, self._app_state)
        self._thread_pool.start(worker)