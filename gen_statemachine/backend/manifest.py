"""
A manifest file is used to describe the files needed to generate a target.

Currently, files in a target directory can be:

- Template files, which require rendering
- Source files, which contain source code in the target language
- Entrypoint files, which may be used to run the final generated code

"""

from enum import Enum
from typing import List, Dict
from pydantic import BaseModel
import tomli
from pathlib import Path

from gen_statemachine.error import ProgramError


class FileType(Enum):
    Unknown = (0,)
    Source = (1,)
    Entrypoint = (2,)
    MakoTemplate = 3


_file_type_tag_map = {
    FileType.Source: ["source"],
    FileType.Entrypoint: ["entrypoint"],
    FileType.MakoTemplate: ["mako template", "mako"],
}


class TargetFile(BaseModel):
    tags: List[str]
    path: str
    destination: str

    def _is_type_of(self, file_type: FileType):
        return any(tag for tag in self.tags if tag in _file_type_tag_map[file_type])

    def is_entrypoint_file(self):
        return self._is_type_of(FileType.Entrypoint)

    def is_mako_template_file(self):
        return self._is_type_of(FileType.MakoTemplate)

    def is_source_file(self):
        return self._is_type_of(FileType.Source)


class TargetManifest(BaseModel):
    target: str
    files: Dict[str, TargetFile]


def load_target_manifest(directory: Path) -> TargetManifest:
    manifest_path = directory / "files.toml"
    if not manifest_path.exists():
        raise ProgramError(f"{directory} does not contain a 'files.toml'")
    manifest_dict = tomli.loads(manifest_path.read_text())
    return TargetManifest(**manifest_dict)
