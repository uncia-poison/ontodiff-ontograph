# ontodiff-ontograph — Auto-Ontographs from Self-Write Memory

This repository extends [`ontodiff`](https://github.com/uncia-poison/ontodiff) with an automated packaging layer that turns self-gathered knowledge into symbolic ontographs.

Install with `python -m pip install -e .`. Export the graph from `ontodiff` using
`IdentityDependencyGraph.to_dict()`, then inspect it with the installed package:

```python
import json
from pathlib import Path
from ontodiff_ontograph import project_identity_graph, render_identity_markdown

graph = json.loads(Path("identity-graph.json").read_text(encoding="utf-8"))
print(render_identity_markdown(project_identity_graph(graph)))
```

## Identity support projection

The package can now consume an identity dependency graph and produce a deterministic,
read-only support map. It exposes which conclusions support current self-state and which
nodes are uncertain, stale, or waiting for reconsolidation.

The projection does not own or rewrite identity. Canonical history stays upstream; this
repository is an inspection and packaging layer.

Identity dependency relations use compact symbols:

- supporting evidence: ⊢
- strict dependency (read source to target): ⇒
- contextual relation: ≈
- identity reconsolidation dependency: ↺

The ↺ relation means that a changed conclusion requires a reviewed self-state
reconsolidation, not automatic deletion.
