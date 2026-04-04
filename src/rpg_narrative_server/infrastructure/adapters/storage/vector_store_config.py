class VectorStoreConfig:
    def __init__(
        self,
        max_file_size_kb: int = 1024,
        max_entries_per_file: int = 1000,
        enable_rotation: bool = True,
    ):
        self.max_file_size_kb = max_file_size_kb
        self.max_entries_per_file = max_entries_per_file
        self.enable_rotation = enable_rotation
