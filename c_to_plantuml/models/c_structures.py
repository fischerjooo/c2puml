from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Field:
    name: str
    type: str
    is_pointer: bool = False
    is_array: bool = False
    array_size: Optional[str] = None

@dataclass
class Function:
    name: str
    return_type: str
    parameters: List[Field]
    is_static: bool = False

@dataclass
class Struct:
    name: str
    fields: List[Field]
    functions: List[Function]
    typedef_name: Optional[str] = None

@dataclass
class Enum:
    name: str
    values: List[str]
    typedef_name: Optional[str] = None 