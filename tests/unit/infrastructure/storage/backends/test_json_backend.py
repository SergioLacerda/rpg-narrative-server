def test_json_backend_builds(tmp_path):

    from rpg_narrative_server.infrastructure.storage.backends.json_backend import (
        JSONStorageBackend,
    )

    backend = JSONStorageBackend(tmp_path)

    vector = backend.build_vector_store()
    doc = backend.build_document_store()

    vector.add("a", [1, 0])

    assert vector.get("a") == [1, 0]

    doc.set("a", {"x": 1})

    assert doc.get("a")["x"] == 1
