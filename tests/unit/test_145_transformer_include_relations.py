#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from c2puml.core.transformer import Transformer
from c2puml.models import ProjectModel, FileModel, IncludeRelation


class TestTransformerIncludeRelations(unittest.TestCase):
    def _make_model(self):
        # Build minimal model: main.c includes a.h and b.h; a.h includes c.h
        files = {}
        files["main.c"] = FileModel(
            file_path="main.c",
            structs={}, enums={}, unions={},
            functions=[], globals=[], includes={"a.h", "b.h"}, macros=[], aliases={},
            include_relations=[], name="main.c"
        )
        files["a.h"] = FileModel(
            file_path="a.h",
            structs={}, enums={}, unions={}, functions=[], globals=[], includes={"c.h"}, macros=[], aliases={},
            include_relations=[], name="a.h"
        )
        files["b.h"] = FileModel(
            file_path="b.h",
            structs={}, enums={}, unions={}, functions=[], globals=[], includes=set(), macros=[], aliases={},
            include_relations=[], name="b.h"
        )
        files["c.h"] = FileModel(
            file_path="c.h",
            structs={}, enums={}, unions={}, functions=[], globals=[], includes=set(), macros=[], aliases={},
            include_relations=[], name="c.h"
        )
        return ProjectModel(project_name="P", source_folder=".", files=files)

    def test_depth_and_filters_with_placeholders(self):
        model = self._make_model()

        with tempfile.TemporaryDirectory() as td:
            # Write model to disk
            model_path = os.path.join(td, "model.json")
            model.save(model_path)

            # Config: depth 2, only keep a.h; always_show_includes True
            cfg = {
                "include_depth": 2,
                "file_specific": {"main.c": {"include_filter": ["^a\\.h$"]}},
                "always_show_includes": True,
            }
            cfg_path = os.path.join(td, "cfg.json")
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f)

            out_path = os.path.join(td, "out.json")
            t = Transformer()
            t.transform(model_path, cfg_path, out_path)

            # Load transformed and assert relations
            from c2puml.models import ProjectModel as PM
            new_model = PM.load(out_path)
            main = new_model.files["main.c"]
            # main.c should have relation to a.h (kept) and b.h as placeholder (relation kept, placeholder set)
            incs = {(rel.source_file, rel.included_file) for rel in main.include_relations}
            self.assertIn(("main.c", "a.h"), incs)
            self.assertIn(("main.c", "b.h"), incs)
            # a.h -> c.h via depth=2
            self.assertIn(("a.h", "c.h"), {(rel.source_file, rel.included_file) for rel in main.include_relations})

            # Placeholder headers should include b.h
            self.assertIn("b.h", getattr(main, "placeholder_headers", set()))


if __name__ == "__main__":
    unittest.main()

