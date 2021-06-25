import pickle
from typing import TYPE_CHECKING, List, Dict

from AoE2ScenarioParser.helper.bytes_parser import slice_bytes
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict
from AoE2ScenarioParser.helper.string_manipulations import add_tabs
from AoE2ScenarioParser.sections.dependencies.dependency import handle_retriever_dependency

if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.retrievers.retriever import Retriever
    from AoE2ScenarioParser.sections.dynamic_retriever_manager import DynamicRetrieverManager as Drm


class SectionDict(dict):
    def __init__(self, d=None, drm=None, parent_path=None, index=-1) -> None:
        """
        Dict object that will notice when given key is not present.

        Args:
            d (dict): dictionary from the start
            drm (Drm): The DynamicRetrieverManager for this scenario
            parent_path (List[str]): The path to the parent in a list with seperated strings
        """
        self.__drm: Drm = drm
        self.__parent_path = [] if parent_path is None else parent_path
        self.__index = index

        super().__init__({} if d is None else d)

    @classmethod
    def from_model(cls, model, set_defaults=False):
        """
        Create a copy (what was called struct before) from a model.

        Args:
            model (AoE2StructModel): The model to copy from
            set_defaults (bool): If retrievers need to be set to the default values

        Returns:
            An SectionDict instance based on the model
        """
        duplicate_rmap = duplicate_retriever_map(model.retriever_map)
        if set_defaults:
            reset_retriever_map(duplicate_rmap)

        return cls(
            d=duplicate_rmap,
            parent_path=model.parent_path + [model.name]
        )

    def set_data_from_bytes(self, data):
        progress = 0
        for retriever in list(self.values()):
            bytes_chunk, p = slice_bytes(retriever, data, progress)
            progress = p
            retriever.set_data_from_bytes(bytes_chunk)

    def get_data_as_bytes(self):
        return b''.join([retriever.get_data_as_bytes() for retriever in self.values()])

    def get(self, key):
        val = super().get(key)
        if val is not None:
            return val
        return self.__solve_missing(key)

    def __getattr__(self, item):
        if item in self.keys():
            return self.get(item).data
        return self.__solve_missing(item)

    def __missing__(self, key):
        return self.__solve_missing(key)

    def __solve_missing(self, key):
        print(f"\n\n>>> Missing value in dict: '{key}'")

        path = self.__parent_path + [key]
        value = self.__drm.determine_value(path)

        return self.setdefault(key, value)

    def __repr__(self) -> str:
        return f"[SectionDict] " + pretty_format_dict(self)

        # parent_list = get_value(self._structure_ref, self.__parent_path)
        # val = get_value(self._structure_ref, path)
        # print(f"key:         {key}")
        # print(f"path:        {path}")
        # print(f"val:         {val}")
        # print(f"parent_list: {parent_list}")
        #
        # if 'type' in val:
        #     return self.__drm.get_value(path[-1], val)
        # else:
        #     return self.setdefault(key, SectionDict(
        #         dynamic_retriever_manager=self.__drm,
        #         parent_path=self.__parent_path + [key]
        #     ))



if __name__ == '__main__':
    a = SectionDict()
    a.setdefault('a', 1)
    a.setdefault('b', 2)
    a.setdefault('c', 3)
    a.setdefault('d', 4)

    x = a['asd2']
    y = a.get('asd')
    z = getattr(a, 'x')

    print(SectionDict({'asdasd': 1, 'asdasda': 2}))


def duplicate_retriever_map(retriever_map: SectionDict[str, 'Retriever']) -> SectionDict[str, 'Retriever']:
    return pickle.loads(pickle.dumps(retriever_map))


def reset_retriever_map(retriever_map: Dict[str, 'Retriever']) -> None:
    for retriever in retriever_map.values():
        retriever.set_data_to_default()
