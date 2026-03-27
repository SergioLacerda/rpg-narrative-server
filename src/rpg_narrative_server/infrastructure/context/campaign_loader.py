from pathlib import Path


class CampaignLoader:

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def load_documents(self) -> list[str]:

        texts = []

        for file in self.base_dir.rglob("*.md"):
            with open(file, encoding="utf-8") as f:
                texts.append(f.read())

        return texts
