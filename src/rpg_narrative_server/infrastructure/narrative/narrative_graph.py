from rpg_narrative_server.utils.json_utils import load_json, save_json
from rpg_narrative_server.infrastructure.nlp.entity_extractor import EntityExtractor

GRAPH_FILE = "data/narrative_graph.json"

entity_extractor = EntityExtractor()


class NarrativeGraph:

    def __init__(self):

        self.graph = load_json(GRAPH_FILE, {})

    def update_from_event(self, text):

        entities = entity_extractor.extract(text)

        for e in entities:

            node = self.graph.setdefault(e, {"links": []})

            for other in entities:

                if other == e:
                    continue

                if other not in node["links"]:
                    node["links"].append(other)

        save_json(GRAPH_FILE, self.graph)

    def related(self, query):

        entities = entity_extractor.extract(query)

        related = set()

        for e in entities:

            node = self.graph.get(e)

            if node:
                related.update(node.get("links", []))

        return related
