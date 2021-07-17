from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.retrievers.retriever import Retriever
    from AoE2ScenarioParser.sections.dynamic_retriever_manager import DynamicRetrieverManager as Drm

class SectionList(list):
    def __init__(self, l=None, drm=None, parent_path=None, index=-1) -> None:
        """
        Dict object that will notice when given key is not present.

        Args:
            l (dict): dictionary from the start
            drm (Drm): The DynamicRetrieverManager for this scenario
            parent_path (List[str]): The path to the parent in a list with seperated strings
        """
        self.__drm: Drm = drm
        self.__parent_path = [] if parent_path is None else parent_path
        self.__index = index

        super().__init__([] if l is None else l)

    def __getitem__(self, i: int):
        return super().__getitem__(i)

    def __solve_missing(self, key):
        print(f"\n\n>>> Missing value in dict: '{key}'")

        path = self.__parent_path + [key]
        value = self.__drm.determine_value(path)

        return self.setdefault(key, value)

