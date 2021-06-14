from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.dynamic_retriever_manager import DynamicRetrieverManager


class RetrieverDict(dict):
    def __init__(self, d=None, drm=None, parent_path=None) -> None:
        """
        Dict object that will notice when given key is not present.

        Args:
            d (dict): dictionary from the start
            drm (DynamicRetrieverManager): The DynamicRetrieverManager for this scenario
            parent_path (List[str]): The path to the parent in a list with seperated strings
        """
        if drm is None:
            raise ValueError("The parameter drm (DynamicRetrieverManager) cannot be None")

        self._drm: DynamicRetrieverManager = drm
        self._parent_path = [] if parent_path is None else parent_path

        # Injected by host
        self._file_section_host = None

        super().__init__({} if d is None else d)

    def get(self, key):
        val = super().get(key)
        if val is not None:
            return val
        return self._solve_missing(key)

    def __getattr__(self, item):
        return self._solve_missing(item)

    def __missing__(self, key):
        return self._solve_missing(key)

    def _solve_missing(self, key):
        print(f"\n\n>>> Missing value in dict: '{key}'")

        if key == 'struct_models':
            raise Exception()

        path = self._parent_path + [key]

        return self._drm.determine_value(path, self._file_section_host)

        # parent_list = get_value(self._structure_ref, self._parent_path)
        # val = get_value(self._structure_ref, path)
        # print(f"key:         {key}")
        # print(f"path:        {path}")
        # print(f"val:         {val}")
        # print(f"parent_list: {parent_list}")
        #
        # if 'type' in val:
        #     return self._drm.get_value(path[-1], val)
        # else:
        #     return self.setdefault(key, RetrieverDict(
        #         dynamic_retriever_manager=self._drm,
        #         parent_path=self._parent_path + [key]
        #     ))


if __name__ == '__main__':
    a = RetrieverDict()
    a.setdefault('a', 1)
    a.setdefault('b', 2)
    a.setdefault('c', 3)
    a.setdefault('d', 4)

    a['asd2']
    a.get('asd')
    getattr(a, 'x')

    print(RetrieverDict({'asdasd': 1, 'asdasda': 2}))
