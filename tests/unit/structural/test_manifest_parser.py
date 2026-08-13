# tests/unit/structural/test_manifest_parser.py

# This file contains unit tests for parsing standard application dependency manifests.

from backend.services.parsers.manifest_parser import ManifestParser


def test_parse_requirements_txt() -> None:
    """Verify dependencies are extracted from requirements.txt."""
    content = "fastapi==0.100.0\npydantic>=2.0\npytest\n"
    parser = ManifestParser()

    dependencies = parser.parse_manifest(content.encode("utf-8"), 123, "requirements.txt")

    deps_map = {d.package_name: d.version_constraint for d in dependencies}
    assert "fastapi" in deps_map
    assert deps_map["fastapi"] == "==0.100.0"
    assert "pydantic" in deps_map
    assert deps_map["pydantic"] == ">=2.0"
    assert "pytest" in deps_map
    assert deps_map["pytest"] is None


def test_parse_package_json() -> None:
    """Verify dependencies are extracted from package.json."""
    content = '{"dependencies": {"react": "^18.2.0"}, "devDependencies": {"jest": "29.0.0"}}'
    parser = ManifestParser()

    dependencies = parser.parse_manifest(content.encode("utf-8"), 123, "package.json")

    deps_map = {d.package_name: d.version_constraint for d in dependencies}
    assert "react" in deps_map
    assert deps_map["react"] == "^18.2.0"
    assert "jest" in deps_map
