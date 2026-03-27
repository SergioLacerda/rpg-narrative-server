class NarrativeGraph:

    def __init__(self):

        self.graph = load_json(GRAPH_FILE, {})

    def update_from_event(self, text):

        entities = extract_entities(text)

        for e in entities:

            node = self.graph.setdefault(e, {"links": []})

            for other in entities:

                if other == e:
                    continue

                if other not in node["links"]:
                    node["links"].append(other)

        save_json(GRAPH_FILE, self.graph)

    def related(self, query):

        entities = extract_entities(query)

        related = set()

        for e in entities:

            node = self.graph.get(e)

            if node:
                related.update(node.get("links", []))

        return related