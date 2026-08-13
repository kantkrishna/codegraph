# tests/unit/structural/test_python_parser.py

# This file contains unit tests for the Tree-sitter Python AST extractor.

from backend.services.parsers.python_parser import PythonParser


def test_python_ast_extraction_classes_and_functions() -> None:
    """Verify that Classes and Functions are deterministically extracted."""
    source_code = """
import os
from pydantic import BaseModel

class UserService:
    \"\"\"Handles user operations.\"\"\"
    def get_user(self, user_id: int):
        pass

def global_helper():
    pass
    """
    parser = PythonParser()
    entities, relationships = parser.parse(source_code.encode("utf-8"), 123, "src/services.py")

    entity_names = {e.name: e for e in entities}
    assert "UserService" in entity_names
    assert entity_names["UserService"].entity_type == "Class"

    assert "get_user" in entity_names
    assert entity_names["get_user"].entity_type == "Function"

    assert "global_helper" in entity_names


def test_python_ast_extraction_imports() -> None:
    """Verify that AST extracts import relationships for US-4.4."""
    source_code = """
import os
import sys
from backend.models import User
    """
    parser = PythonParser()
    entities, relationships = parser.parse(source_code.encode("utf-8"), 123, "src/main.py")

    targets = [r.target_module for r in relationships if r.relationship_type == "IMPORTS"]
    assert "os" in targets
    assert "sys" in targets
    assert "backend.models" in targets
