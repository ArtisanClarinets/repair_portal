from repair_portal.core import codebase_map


def test_build_inventory_creates_output(tmp_path, monkeypatch):
    monkeypatch.setattr(codebase_map, "BUILD_DIR", tmp_path)
    monkeypatch.setattr(codebase_map, "OUTPUT_PATH", tmp_path / "cross_module_map.json")

    inventory = codebase_map.build_inventory()
    assert inventory.doctypes

    codebase_map.main()
    assert (tmp_path / "cross_module_map.json").exists()
