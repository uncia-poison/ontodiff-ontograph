# ontodiff-ontograph — Auto-Ontographs from Self-Write Memory

This repository extends [`ontodiff`](https://github.com/uncia-poison/ontodiff) with an automated packaging layer that turns self-gathered knowledge into symbolic ontographs.

It includes:

- **Symbol allocator**: picks stable Unicode symbols (with a small emoji fallback) for each concept type and persists assignments in `data/symbols.json`.
- **Ontology graph builder**: mines self-memory rules, de-duplicates candidate nodes, builds a directed ontograph, and weights edges based on conditional probabilities.
- **KaiScriptor exporter**: dumps the graph as a KaiScriptor code block and a human-readable Markdown proposal in `proposals/`.

The first layer (self-write gate & memory) lives in the [`ontodiff`](https://github.com/uncia-poison/ontodiff) repository.

## Quickstart

```bash
pip install -e .
python -m ontodiff.cli examples/sample_chat.jsonl --root .
python -c "import ontodiff.ontograph.migrate_emoji as m; m.migrate_json_events('.')"
python -c "import ontodiff.ontograph.packager as p; print(p.run('.'))"
```


## Identity support projection

The package can now consume an identity dependency graph and produce a deterministic,
read-only support map. It exposes which conclusions support current self-state and which
nodes are uncertain, stale, or waiting for reconsolidation.

The projection does not own or rewrite identity. Canonical history stays upstream; this
repository is an inspection and packaging layer.

Identity dependency relations use compact symbols:

- supporting/hard dependency: ⊢
- contextual relation: ≈
- identity reconsolidation dependency: ↺

The ↺ relation means that a changed conclusion requires a reviewed self-state
reconsolidation, not automatic deletion.
