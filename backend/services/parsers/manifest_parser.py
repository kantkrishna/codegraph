# backend/services/parsers/manifest_parser.py

# Parses application manifests (requirements.txt, package.json) for dependencies.

import json
import re
import yaml
from backend.models.events import DependencyDetected

class ManifestParser:
    def parse_manifest(self, content: bytes, repo_id: int, file_path: str) -> list[DependencyDetected]:
        text = content.decode("utf-8", errors="ignore")
        dependencies: list[DependencyDetected] = []
        
        if file_path.endswith("requirements.txt"):
            for line in text.splitlines():
                line = line.split("#")[0].strip()
                if not line: continue
                match = re.match(r"^([a-zA-Z0-9_\-]+)([=><~^]+.*)?$", line)
                if match:
                    dependencies.append(DependencyDetected(
                        repository_id=repo_id, file_path=file_path,
                        package_manager="pip", package_name=match.group(1),
                        version_constraint=match.group(2)
                    ))
        elif file_path.endswith("package.json"):
            try:
                data = json.loads(text)
                for key in ["dependencies", "devDependencies"]:
                    if key in data:
                        for pkg, ver in data[key].items():
                            dependencies.append(DependencyDetected(
                                repository_id=repo_id, file_path=file_path,
                                package_manager="npm", package_name=pkg,
                                version_constraint=ver
                            ))
            except json.JSONDecodeError:
                pass
        
        # FIX 3: Safe DOM-based Kubernetes Topology Parsing
        elif file_path.endswith((".yaml", ".yml")):
            try:
                docs = yaml.safe_load_all(text)
                # Known macro-architecture services in the demo
                known_services = [
                    "frontend", "cartservice", "productcatalogservice", 
                    "currencyservice", "paymentservice", "shippingservice", 
                    "emailservice", "checkoutservice", "recommendationservice", 
                    "adservice", "redis-cart"
                ]
                for doc in docs:
                    if not doc or not isinstance(doc, dict):
                        continue
                    
                    kind = doc.get("kind")
                    if kind in ("Deployment", "StatefulSet"):
                        source_svc = doc.get("metadata", {}).get("name")
                        if not source_svc:
                            continue
                            
                        # Dump deployment spec to string to quickly scan env var network references
                        doc_str = json.dumps(doc).lower()
                        
                        for target in known_services:
                            if target == source_svc:
                                continue
                            
                            # Matches references like "value": "emailservice:5000"
                            if f'"{target}:' in doc_str or f'"{target}"' in doc_str:
                                dependencies.append(
                                    DependencyDetected(
                                        repository_id=repo_id,
                                        file_path=file_path,
                                        package_manager="kubernetes",
                                        package_name=target,
                                        version_constraint=source_svc
                                    )
                                )
            except Exception:
                pass

        return dependencies