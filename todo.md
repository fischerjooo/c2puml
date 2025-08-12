# Test Enhancement TODO (Pending Only)

## Pending
- Integration tests: consider adding `relationships_exist` and class/relationship counts where output patterns are stable
- Add more negative assertions (`functions_not_exist`, `structs_not_exist`) in selected feature/example tests where meaningful
- Audit remaining tests for `model.project_name` and `element_counts.files`; add where missing
- Prefer per-file `puml.files.contains_lines` for stable checks; expand in any tests that still rely on global `contains_elements`
- Add minimal `files` assertions (`./output/model.json`, `./output/model_transformed.json`) where safe

Last updated: 2025-08-12