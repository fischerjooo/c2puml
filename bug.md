### Include relations are nondeterministic across runs

- **Impact**: Include arrows in generated `.puml` files sometimes flip direction or disappear/reappear between runs with the exact same sources and configuration.
- **Symptoms observed**: Differences in header-to-header includes in `sample.puml`, `sample2.puml`, and occasionally additional/missing edges in `application.puml`.
- **Reproducibility**: Reproduced locally by running the pipeline twice with different `PYTHONHASHSEED` values.

### How to reproduce locally

1) Create two configs writing to distinct output directories (or duplicate the example config and change `output_dir`).

```bash
# Run A
PYTHONHASHSEED=0 python3 main.py --config tests/example/config.json --verbose
# Save or copy artifacts/output_example -> tmp/runA

# Run B
PYTHONHASHSEED=123 python3 main.py --config tests/example/config.json --verbose
# Save or copy artifacts/output_example -> tmp/runB
```

2) Compare include arrows only:

```bash
for f in tmp/runA/*.puml; do bn=$(basename "$f"); \
  echo "== $bn =="; \
  echo "-- A --"; grep '<<include>>' "$f" | sort; \
  echo "-- B --"; grep '<<include>>' "tmp/runB/$bn" | sort; echo; done
```

### Evidence (from local spike)

- `sample.puml` differences:
```plantuml
-- A --
HEADER_GEOMETRY --> HEADER_SAMPLE : <<include>>
HEADER_LOGGER --> HEADER_CONFIG : <<include>>
HEADER_MATH_UTILS --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_CONFIG : <<include>>
SAMPLE --> HEADER_GEOMETRY : <<include>>
SAMPLE --> HEADER_LOGGER : <<include>>
SAMPLE --> HEADER_MATH_UTILS : <<include>>
SAMPLE --> HEADER_SAMPLE : <<include>>
-- B --
HEADER_LOGGER --> HEADER_CONFIG : <<include>>
HEADER_MATH_UTILS --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_GEOMETRY : <<include>>
HEADER_SAMPLE --> HEADER_LOGGER : <<include>>
SAMPLE --> HEADER_GEOMETRY : <<include>>
SAMPLE --> HEADER_LOGGER : <<include>>
SAMPLE --> HEADER_MATH_UTILS : <<include>>
SAMPLE --> HEADER_SAMPLE : <<include>>
```

- `sample2.puml` differences:
```plantuml
-- A --
HEADER_FIRST_LEVEL --> HEADER_FILTERED_HEADER : <<include>>
HEADER_GEOMETRY --> HEADER_SAMPLE : <<include>>
HEADER_LOGGER --> HEADER_CONFIG : <<include>>
HEADER_MATH_UTILS --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_CONFIG : <<include>>
SAMPLE2 --> HEADER_FILTERED_HEADER : <<include>>
SAMPLE2 --> HEADER_FIRST_LEVEL : <<include>>
SAMPLE2 --> HEADER_GEOMETRY : <<include>>
SAMPLE2 --> HEADER_LOGGER : <<include>>
SAMPLE2 --> HEADER_MATH_UTILS : <<include>>
SAMPLE2 --> HEADER_SAMPLE : <<include>>
-- B --
HEADER_FIRST_LEVEL --> HEADER_FILTERED_HEADER : <<include>>
HEADER_LOGGER --> HEADER_CONFIG : <<include>>
HEADER_MATH_UTILS --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_CONFIG : <<include>>
HEADER_SAMPLE --> HEADER_GEOMETRY : <<include>>
HEADER_SAMPLE --> HEADER_LOGGER : <<include>>
SAMPLE2 --> HEADER_FILTERED_HEADER : <<include>>
SAMPLE2 --> HEADER_FIRST_LEVEL : <<include>>
SAMPLE2 --> HEADER_GEOMETRY : <<include>>
SAMPLE2 --> HEADER_LOGGER : <<include>>
SAMPLE2 --> HEADER_MATH_UTILS : <<include>>
SAMPLE2 --> HEADER_SAMPLE : <<include>>
```

- `application.puml` occasionally shows an extra edge in one run:
```plantuml
-- A --
APPLICATION --> HEADER_COMMON : <<include>>
APPLICATION --> HEADER_DATABASE : <<include>>
APPLICATION --> HEADER_NETWORK : <<include>>
HEADER_DATABASE --> HEADER_LIBPQ_FE : <<include>>
HEADER_DATABASE --> HEADER_MYSQL : <<include>>
HEADER_DATABASE --> HEADER_SQLITE3 : <<include>>
HEADER_NETWORK --> HEADER_COMMON : <<include>>
-- B --
APPLICATION --> HEADER_COMMON : <<include>>
APPLICATION --> HEADER_DATABASE : <<include>>
APPLICATION --> HEADER_NETWORK : <<include>>
HEADER_DATABASE --> HEADER_COMMON : <<include>>   # appears only in B
HEADER_DATABASE --> HEADER_LIBPQ_FE : <<include>>
HEADER_DATABASE --> HEADER_MYSQL : <<include>>
HEADER_DATABASE --> HEADER_SQLITE3 : <<include>>
HEADER_NETWORK --> HEADER_COMMON : <<include>>
```

### Root cause analysis

- The include processing BFS iterates over `FileModel.includes`, which is a `set`, leading to nondeterministic iteration order that depends on hash seed.
```1:250:src/c2puml/models.py
# ... existing code ...
class FileModel:
    # ... existing code ...
    includes: Set[str] = field(default_factory=set)
    # ... existing code ...
```

- In the BFS, relations are skipped entirely when the target header was already processed in the current traversal, causing legitimate reverse edges in mutually-including headers to be dropped depending on traversal order.
```496:577:src/c2puml/core/transformer.py
                # Process each include in the current file
                for include_name in current_file.includes:
                    # ... existing code ...
                    # Prevent self-references
                    if include_name == current_filename:
                        # ... existing code ...
                        continue
                    
                    # Check for duplicate relations to prevent cycles
                    existing_relation = any(
                        rel.source_file == current_filename and rel.included_file == include_name
                        for rel in root_file.include_relations
                    )
                    
                    if existing_relation:
                        # ... existing code ...
                        continue
                    
                    # Prevent processing files that would create cycles (already processed)
                    if include_name in processed_files:
                        # NOTE: This also prevents adding a valid reverse edge when two headers include each other
                        # depending on which one was processed first at this depth.
                        continue
                    
                    # Create and add the include relation to the root C file
                    relation = IncludeRelation(
                        source_file=current_filename,
                        included_file=include_name,
                        depth=depth
                    )
                    root_file.include_relations.append(relation)
                    # ... existing code ...
```

- Because both the iteration over `includes` and the construction of `next_level` are influenced by set ordering, the first header visited in a mutual-include pair “wins,” and the reverse edge is skipped. Different seeds → different visit order → different set of edges.

### Contributing factors
- Use of `Set[str]` for `FileModel.includes` (unordered).
- Iterating includes without sorting: `for include_name in current_file.includes:`.
- Skipping edge creation when `include_name in processed_files` instead of only preventing re-processing of content.
- Building the next frontier (`next_level`) from unordered inputs.

### Recommendations (deterministic and complete)

1) Make traversal deterministic at every step:
   - Iterate includes in sorted order: `for include_name in sorted(current_file.includes):`
   - Sort `next_level` by filename before the next depth: `next_level.sort(key=lambda fm: Path(fm.name).name)`
   - Process root C files in a stable order: `for root_file in sorted(c_files, key=lambda fm: fm.name):`

2) Do not suppress legitimate edges:
   - Keep the cycle-prevention for traversal, but still add the edge even if `include_name in processed_files`. Only skip adding `included_file` to `next_level` to avoid infinite traversal.
   - Alternatively track edges in a `seen_edges` set `{(source, target)}` to de-duplicate edges, rather than blocking on `processed_files`.

3) Consider preserving include declaration order:
   - Change `FileModel.includes` to `List[str]` (maintain source order) and only de-duplicate after preserving order, or maintain a stable ordered set abstraction.

4) Keep final output stable:
   - Continue sorting edges at emission time (already done in generator), but ensure the underlying relation set is complete and deterministically built.

### Quick spike to validate a fix (suggested)

- After applying (1) and (2), repeat the two-run comparison above. The `grep '<<include>>' | sort` output must be identical across runs for all `.puml` files.
- Add a small CI check that runs the example twice with two seeds and diffs the normalized include lines to guard against regressions.

### Notes
- The generator already sorts `include_relations` when emitting edges, but sorting cannot recover edges that were skipped during traversal. The fix must happen in the transformer’s include-processing BFS.