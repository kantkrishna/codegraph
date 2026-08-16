# backend/services/parsers/python_parser.py

# Implements resilient Tree-sitter AST extraction for Python files using DFS traversal.

from typing import Any

import tree_sitter_python as tspy
from tree_sitter import Language, Parser

from backend.models.events import EntityExtracted, RelationshipExtracted
from backend.services.parsers.base import BaseASTParser


class PythonParser(BaseASTParser):
    def __init__(self) -> None:
        self.language = Language(tspy.language())
        self.parser = Parser(self.language)

    def parse(
        self, source_code: bytes, repo_id: int, file_path: str
    ) -> tuple[list[EntityExtracted], list[RelationshipExtracted]]:
        tree = self.parser.parse(source_code)
        entities: list[EntityExtracted] = []
        relationships: list[RelationshipExtracted] = []

        def traverse(node: Any) -> None:
            # 1. Extract Classes
            if node.type == "class_definition":
                for child in node.children:
                    if child.type == "identifier":
                        # Bulletproof byte-slicing (Immune to node.text API changes)
                        text = source_code[child.start_byte : child.end_byte].decode(
                            "utf-8", errors="ignore"
                        )
                        entities.append(
                            EntityExtracted(
                                repository_id=repo_id,
                                file_path=file_path,
                                entity_type="Class",
                                name=text,
                            )
                        )
                        break

            # 2. Extract Functions
            elif node.type == "function_definition":
                for child in node.children:
                    if child.type == "identifier":
                        text = source_code[child.start_byte : child.end_byte].decode(
                            "utf-8", errors="ignore"
                        )
                        entities.append(
                            EntityExtracted(
                                repository_id=repo_id,
                                file_path=file_path,
                                entity_type="Function",
                                name=text,
                            )
                        )
                        break

            # 3. Extract Standard Imports
            elif node.type == "import_statement":

                def extract_dotted(n: Any) -> None:
                    if n.type == "dotted_name":
                        text = source_code[n.start_byte : n.end_byte].decode(
                            "utf-8", errors="ignore"
                        )
                        relationships.append(
                            RelationshipExtracted(
                                repository_id=repo_id,
                                source_file=file_path,
                                target_module=text,
                                relationship_type="IMPORTS",
                            )
                        )
                    else:
                        for c in n.children:
                            extract_dotted(c)

                extract_dotted(node)

            # 4. Extract From Imports
            elif node.type == "import_from_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        text = source_code[child.start_byte : child.end_byte].decode(
                            "utf-8", errors="ignore"
                        )
                        relationships.append(
                            RelationshipExtracted(
                                repository_id=repo_id,
                                source_file=file_path,
                                target_module=text,
                                relationship_type="IMPORTS",
                            )
                        )
                        break

            # Continue deep search
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return entities, relationships
