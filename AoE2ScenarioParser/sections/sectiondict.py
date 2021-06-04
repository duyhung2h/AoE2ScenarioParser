from AoE2ScenarioParser.sections.retriever_reader import get_value, func


class SectionDict(dict):
    def __init__(self, d=None, structure_ref=None, vr_manager=None, parent_path=None) -> None:
        if d is None:
            d = {}
        if structure_ref is None:
            structure_ref = {}
        if parent_path is None:
            parent_path = []
        if vr_manager is None:
            raise ValueError("The attribute vr_manager is mandatory")

        self._structure_ref = structure_ref
        self._vr_manager = vr_manager
        self._parent_path = parent_path

        super().__init__(d)

    def get(self, key):
        val = super().get(key)
        if val is not None:
            return val
        return self.__missing__(key)

    def __getattr__(self, item):
        return self.__missing__(item)

    def __missing__(self, key):
        path = self._parent_path + [key]
        val = get_value(self._structure_ref, path)

        if 'type' in val:
            return func(self._structure_ref, self._vr_manager, val)
        else:
            return self.setdefault(key, SectionDict(
                structure_ref=self._structure_ref,
                vr_manager=self._vr_manager,
                parent_path=self._parent_path + [key]
            ))


if __name__ == '__main__':
    a = SectionDict()
    a.setdefault('a', 1)
    a.setdefault('b', 2)
    a.setdefault('c', 3)
    a.setdefault('d', 4)

    a['asd2']
    a.get('asd')
    getattr(a, 'x')

    print(SectionDict({'asdasd': 1, 'asdasda': 2}))
