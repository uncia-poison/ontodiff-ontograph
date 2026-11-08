from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

SOURCE_SCHEMA = "ontodiff.identity-dependency.v1"
RELATION_SYMBOLS = {
    "hard": "⊢",
    "supporting": "⊢",
    "contextual": "≈",
    "identity": "↺",
}


class IdentityGraphProjectionError(ValueError):
    pass


def _required_string(value: Any, field: str) -> str:
    if type(value) is not str or not value:
        raise IdentityGraphProjectionError(f"{field} must be a non-empty string")
    return value


def project_identity_graph(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Create a deterministic read-only support map from an identity graph."""
    if payload.get("schema_version") != SOURCE_SCHEMA:
        raise IdentityGraphProjectionError("unsupported identity dependency schema")
    raw_nodes = payload.get("nodes", [])
    raw_edges = payload.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise IdentityGraphProjectionError("nodes and edges must be lists")

    nodes: dict[str, dict[str, Any]] = {}
    for raw in raw_nodes:
        if not isinstance(raw, Mapping):
            raise IdentityGraphProjectionError("node must be a mapping")
        node_id = _required_string(raw.get("node_id"), "node_id")
        if node_id in nodes:
            raise IdentityGraphProjectionError(f"duplicate node_id: {node_id}")
        nodes[node_id] = {
            "node_id": node_id,
            "kind": _required_string(raw.get("kind"), "kind"),
            "status": _required_string(raw.get("status", "active"), "status"),
            "confidence": float(raw.get("confidence", 1.0)),
            "label": str(raw.get("label", "")),
            "metadata": deepcopy(dict(raw.get("metadata", {}))),
            "incoming": [],
            "outgoing": [],
        }

    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for raw in raw_edges:
        if not isinstance(raw, Mapping):
            raise IdentityGraphProjectionError("edge must be a mapping")
        source = _required_string(raw.get("source_id"), "source_id")
        target = _required_string(raw.get("target_id"), "target_id")
        kind = _required_string(raw.get("kind"), "kind")
        if source not in nodes or target not in nodes:
            raise IdentityGraphProjectionError("edge references an unknown node")
        if kind not in RELATION_SYMBOLS:
            raise IdentityGraphProjectionError(f"unsupported edge kind: {kind}")
        key = (source, target, kind)
        if key in seen:
            continue
        seen.add(key)
        edge = {
            "source_id": source,
            "target_id": target,
            "kind": kind,
            "symbol": RELATION_SYMBOLS[kind],
            "weight": float(raw.get("weight", 1.0)),
            "context": raw.get("context"),
        }
        edges.append(edge)
        nodes[source]["outgoing"].append(target)
        nodes[target]["incoming"].append(source)

    return {
        "schema_version": "ontodiff.ontograph.identity-projection.v1",
        "source_schema": SOURCE_SCHEMA,
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": sorted(edges, key=lambda e: (e["source_id"], e["target_id"], e["kind"])),
        "identity_nodes": sorted(
            node_id for node_id, node in nodes.items() if node["kind"] == "self_state"
        ),
        "review_queue": sorted(
            node_id
            for node_id, node in nodes.items()
            if node["status"] in {"review", "uncertain", "stale", "reconsolidate"}
        ),
    }


def render_kaiscriptor_relations(projection: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for edge in projection.get("edges", []):
        if isinstance(edge, Mapping):
            source = str(edge.get("source_id", ""))
            target = str(edge.get("target_id", ""))
            symbol = str(edge.get("symbol", "≈"))
            if source and target:
                lines.append(f"{source} {symbol} {target}")
    return "\n".join(lines)


def render_identity_markdown(projection: Mapping[str, Any]) -> str:
    nodes = {
        str(node["node_id"]): node
        for node in projection.get("nodes", [])
        if isinstance(node, Mapping) and "node_id" in node
    }
    lines = [
        "# Identity support map",
        "",
        "Read-only projection: this view does not rewrite identity.",
        "",
        "## Current self-state nodes",
    ]
    for node_id in projection.get("identity_nodes", []):
        node = nodes.get(str(node_id), {})
        lines.append(
            f"- {node_id}: {node.get('status', 'unknown')} "
            f"(confidence {float(node.get('confidence', 0.0)):.2f})"
        )
    lines.extend(["", "## Review / reconsolidation queue"])
    queue = list(projection.get("review_queue", []))
    if queue:
        for node_id in queue:
            node = nodes.get(str(node_id), {})
            lines.append(f"- {node_id}: {node.get('status', 'unknown')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Dependencies", "", render_kaiscriptor_relations(projection) or "(none)"])
    return "\n".join(lines) + "\n"
