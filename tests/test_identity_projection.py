from ontodiff_ontograph import (
    project_identity_graph,
    render_identity_markdown,
    render_kaiscriptor_relations,
)


def fixture():
    return {
        "schema_version": "ontodiff.identity-dependency.v1",
        "nodes": [
            {"node_id": "e1", "kind": "evidence", "status": "active", "confidence": 1.0},
            {"node_id": "c1", "kind": "conclusion", "status": "uncertain", "confidence": 0.7},
            {"node_id": "s1", "kind": "self_state", "status": "reconsolidate", "confidence": 0.8},
        ],
        "edges": [
            {"source_id": "e1", "target_id": "c1", "kind": "supporting", "weight": 0.8},
            {"source_id": "c1", "target_id": "s1", "kind": "identity", "weight": 1.0},
        ],
    }


def test_projection_surfaces_identity_and_review_queue():
    result = project_identity_graph(fixture())
    assert result["identity_nodes"] == ["s1"]
    assert result["review_queue"] == ["c1", "s1"]


def test_projection_renders_support_and_reconsolidation_edges():
    result = project_identity_graph(fixture())
    text = render_kaiscriptor_relations(result)
    assert "e1 ⊢ c1" in text
    assert "c1 ↺ s1" in text


def test_markdown_is_read_only_inspection_report():
    text = render_identity_markdown(project_identity_graph(fixture()))
    assert "Read-only projection" in text
    assert "s1" in text
    assert "reconsolidate" in text

def test_projection_keeps_distinct_edges_and_is_order_independent():
    payload = fixture()
    payload["edges"].append(dict(payload["edges"][0], context="alternate support"))
    first = project_identity_graph(payload)
    payload["edges"].reverse()
    payload["nodes"].reverse()
    assert project_identity_graph(payload) == first
    assert len(first["edges"]) == 3
