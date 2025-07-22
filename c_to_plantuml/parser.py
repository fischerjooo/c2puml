#!/usr/bin/env python3
"""
Parser module for C to PlantUML converter - Step 1: Parse C code files and generate model.json

REFACTORED: Now uses pycparser-based parsing instead of tokenizer-based parsing
"""

import logging
from pathlib import Path
from typing import Dict, List

from .models import FileModel, ProjectModel, Struct, Enum, Function, Field
from .utils import detect_file_encoding
from .pycparser_driver import parse_c_file

class CParser:
    """C/C++ parser for extracting structural information from source code using pycparser"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_project(self, project_root: str, recursive: bool = True) -> ProjectModel:
        """Parse a C/C++ project and return a model"""
        project_root = Path(project_root).resolve()
        if not project_root.exists():
            raise ValueError(f"Project root not found: {project_root}")
        if not project_root.is_dir():
            raise ValueError(f"Project root must be a directory: {project_root}")
        self.logger.info(f"Parsing project: {project_root}")
        c_files = self._find_c_files(project_root, recursive)
        self.logger.info(f"Found {len(c_files)} C/C++ files")
        files = {}
        failed_files = []
        for file_path in c_files:
            try:
                relative_path = str(file_path.relative_to(project_root))
                file_model = self.parse_file(file_path, relative_path, str(project_root))
                files[relative_path] = file_model
                self.logger.debug(f"Successfully parsed: {relative_path}")
            except Exception as e:
                self.logger.warning(f"Failed to parse {file_path}: {e}")
                failed_files.append(str(file_path))
        if failed_files:
            error_msg = (
                f"Failed to parse {len(failed_files)} files: {failed_files}. "
                "Stopping model processing."
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        model = ProjectModel(
            project_name=project_root.name,
            project_root=str(project_root),
            files=files,
        )
        self.logger.info(f"Parsing complete. Parsed {len(files)} files successfully.")
        return model

    def parse_file(self, file_path: Path, relative_path: str, project_root: str) -> FileModel:
        """Parse a single C/C++ file and return a file model using pycparser"""
        self.logger.debug(f"Parsing file: {file_path}")
        encoding = detect_file_encoding(file_path)
        model_dict = parse_c_file(file_path)
        # Convert pycparser_driver model to FileModel
        structs = {}
        for s in model_dict.get("structs", []):
            fields = [Field(name=f["name"], type=f["type"]) for f in s.get("fields", [])]
            structs[s["name"]] = Struct(name=s["name"], fields=fields)
        enums = {}
        for e in model_dict.get("enums", []):
            enums[e["name"]] = Enum(name=e["name"], values=e.get("values", []))
        functions = []
        for f in model_dict.get("functions", []):
            params = [Field(name=p["name"], type=p["type"]) for p in f.get("params", [])]
            functions.append(Function(name=f["name"], return_type=f["return_type"], parameters=params))
        typedefs = {t["name"]: t["type"] for t in model_dict.get("typedefs", [])}
        # TODO: Fill in other fields (globals, includes, macros, typedef_relations, etc.)
        return FileModel(
            file_path=str(file_path),
            relative_path=relative_path,
            project_root=project_root,
            encoding_used=encoding,
            structs=structs,
            enums=enums,
            functions=functions,
            typedefs=typedefs,
        )

    def _find_c_files(self, project_root: Path, recursive: bool) -> List[Path]:
        """Find all .c files in the project root (optionally recursively)"""
        if recursive:
            return [p for p in project_root.rglob("*.c") if p.is_file()]
        else:
            return [p for p in project_root.glob("*.c") if p.is_file()]

class Parser:
    """Main parser class for Step 1: Parse C code files and generate model.json"""
    def __init__(self):
        self.c_parser = CParser()
        self.logger = logging.getLogger(__name__)
    def parse(self, project_root: str, output_file: str = "model.json", recursive: bool = True) -> str:
        self.logger.info(f"Step 1: Parsing C/C++ project: {project_root}")
        try:
            model = self.c_parser.parse_project(project_root, recursive)
        except RuntimeError as e:
            self.logger.error(f"Failed to parse project: {e}")
            raise
        model.save(output_file)
        self.logger.info(f"Step 1 complete! Model saved to: {output_file}")
        self.logger.info(f"Found {len(model.files)} files")
        total_structs = sum(len(f.structs) for f in model.files.values())
        total_enums = sum(len(f.enums) for f in model.files.values())
        total_functions = sum(len(f.functions) for f in model.files.values())
        self.logger.info(
            f"Summary: {total_structs} structs, {total_enums} enums, "
            f"{total_functions} functions"
        )
        return output_file
