from __future__ import annotations

from typing import Dict, TYPE_CHECKING

from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever

if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.variable_retriever_manager import DynamicRetrieverManager


class AoE2StructModel:
    def __init__(self, name, retriever_map, structs, drm):
        """
        A model to create file section structs.

        Args:
            name (str): The name
            retriever_map (Dict[str, Retriever]): The retriever map associated with it
            structs (Dict[AoE2StructModel]): The possible sub-struct models
            drm (DynamicRetrieverManager): The DynamicRetrieverManager for this scenario
        """
        self.name = name
        self.retriever_map = retriever_map
        self.structs = structs
        self.drm = drm

    @classmethod
    def from_structure(cls, name, structure, drm) -> AoE2StructModel:
        retriever_map = {}
        for retriever_name, attr in structure.get('retrievers').items():
            retriever_map[retriever_name] = Retriever.from_structure(attr, retriever_name)
        structs = model_dict_from_structure(structure, drm)

        return cls(name, retriever_map, structs, drm)

    def __str__(self):
        return f"[AoE2StructModel] {self.name} -> retrievers: " + pretty_format_dict(self.retriever_map)


def model_dict_from_structure(structure, drm) -> Dict[AoE2StructModel]:
    models = {}
    for name, attr in structure.get('structs', {}).items():
        # Create struct model
        models[name] = AoE2StructModel.from_structure(name, attr, drm)
    return models
