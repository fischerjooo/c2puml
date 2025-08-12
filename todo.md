# Test Enhancement TODO (Pending Only)

## Pending
- Expand per-file `puml.files.contains_lines` where stable; reduce reliance on `contains_elements` where possible
- Add selective negative assertions (`functions_not_exist`, `structs_not_exist`) in scenarios designed to exclude elements
- Audit remaining tests for missing `model.project_name` and `element_counts.files` (most covered; spot-check new/edge cases)
- Ensure `files` assertions include both `./output/model.json` and `./output/model_transformed.json` where applicable

Last updated: 2025-08-12