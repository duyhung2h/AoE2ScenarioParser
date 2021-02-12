from AoE2ScenarioParser.helper.datatype import DataType
from AoE2ScenarioParser.helper.retriever import Retriever
from AoE2ScenarioParser.pieces.aoe2_file_section import AoE2FileSection


class VariableStruct(AoE2FileSection):
    def __init__(self):
        retrievers = [
            Retriever("variable_id", DataType("u32")),
            Retriever("name", DataType("str32")),
        ]

        super().__init__("Variable", retrievers)

    @staticmethod
    def defaults(pieces):
        defaults = {
            'variable_id': 0,
            'name': '_Variable0',
        }
        return defaults
