from pathlib import Path

from rpg_narrative_server.infrastructure.storage.json_utils import read_json, write_json


def test_read_json_file_not_exists(tmp_path):

    path = tmp_path / "file.json"

    result = read_json(path, default={})

    assert result == {}


def test_read_json_valid(tmp_path):

    path = tmp_path / "file.json"
    path.write_text('{"a": 1}')

    result = read_json(path, default={})

    assert result["a"] == 1


def test_read_json_invalid(tmp_path):

    path = tmp_path / "file.json"
    path.write_text("invalid json")

    result = read_json(path, default={})

    assert result == {}


def test_write_json(tmp_path):

    path = tmp_path / "dir" / "file.json"

    write_json(path, {"x": 1})

    assert path.exists()
    assert "x" in path.read_text()