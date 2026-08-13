# backend/services/parsers/base.py

# Defines the abstract base class for all language-specific AST parsers.

from abc import ABC, abstractmethod

from backend.models.events import EntityExtracted, RelationshipExtracted


class BaseASTParser(ABC):
    @abstractmethod
    def parse(
        self, source_code: bytes, repo_id: int, file_path: str
    ) -> tuple[list[EntityExtracted], list[RelationshipExtracted]]:
        """Parses source code and returns structural entities and relationships."""
        pass
