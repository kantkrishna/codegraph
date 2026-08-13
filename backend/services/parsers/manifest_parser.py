# backend/services/parsers/manifest_parser.py

# Parses application manifests (requirements.txt, package.json) for dependencies.

import json
import re

from backend.models.events import DependencyDetected


class ManifestParser:
    def parse_manifest(
        self, content: bytes, repo_id: int, file_path: str
    ) -> list[DependencyDetected]:
        text = content.decode("utf-8", errors="ignore")
        dependencies: list[DependencyDetected] = []

        if file_path.endswith("requirements.txt"):
            for line in text.splitlines():
                line = line.split("#")[0].strip()
                if not line:
                    continue
                # Match package name and version constraints (e.g. fastapi==0.100.0)
                match = re.match(r"^([a-zA-Z0-9_\-]+)([=><~^]+.*)?$", line)
                if match:
                    pkg_name = match.group(1)
                    constraint = match.group(2) if match.group(2) else None
                    dependencies.append(
                        DependencyDetected(
                            repository_id=repo_id,
                            file_path=file_path,
                            package_name=pkg_name,
                            version_constraint=constraint,
                        )
                    )

        elif file_path.endswith("package.json"):
            try:
                data = json.loads(text)
                for key in ["dependencies", "devDependencies"]:
                    if key in data:
                        for pkg, ver in data[key].items():
                            dependencies.append(
                                DependencyDetected(
                                    repository_id=repo_id,
                                    file_path=file_path,
                                    package_name=pkg,
                                    version_constraint=ver,
                                )
                            )
            except json.JSONDecodeError:
                pass

        return dependencies
