from __future__ import annotations

from typing import List

from AoE2ScenarioParser.helper import bytes_parser, string_manipulations
from AoE2ScenarioParser.helper.bytes_conversions import parse_bytes_to_val, parse_val_to_bytes
from AoE2ScenarioParser.helper.bytes_parser import slice_bytes
from AoE2ScenarioParser.helper.list_functions import listify
from AoE2ScenarioParser.helper.pretty_format import pretty_format_list, pretty_format_dict
from AoE2ScenarioParser.helper.string_manipulations import add_tabs
from AoE2ScenarioParser.sections.dependencies.dependency_action import DependencyAction
from AoE2ScenarioParser.sections.dependencies.retriever_dependency import RetrieverDependency
from AoE2ScenarioParser.sections.retrievers.datatype import DataType
from AoE2ScenarioParser.sections.sectiondict import SectionDict


class Retriever:
    """ A Class for defining how to retrieve data.
    The Constructor has quite some parameters which can all be used for getting the proper data
    """

    __slots__ = [
        'on_construct',
        'on_commit',
        'on_refresh',
        'name',
        'datatype',
        'is_list',
        'log_value',
        '_data',
        '_data_as_bytes',
        '_model',
        'default_value'
    ]

    on_construct: RetrieverDependency
    on_commit: RetrieverDependency
    on_refresh: RetrieverDependency

    def __init__(self, name, default_value, datatype=DataType(), is_list=None, log_value=False):
        """
        Args:
            name (str): The name of the item. Has to be unique within the Section or Struct
            default_value (Any): The default value of this retriever
            datatype (DataType): A datatype object
            is_list (Union[None, bool]): If this retriever data should be presented using a list. If None, it's unknown.
            log_value (bool): A boolean for, mostly, debugging. This will log information about this retrievers when the
                data is changed, when this retriever is constructed and when it's committed.
        """
        self.name: str = name
        self.default_value = default_value
        self.datatype: DataType = datatype
        self.is_list = is_list
        self.log_value = log_value
        self._data = None
        self._data_as_bytes = None
        self._model = None

        if log_value:
            self.datatype.log_value = True
            self.datatype._debug_retriever_name = name

    @property
    def data(self):
        # Using try-except instead of an if statement for performance reasons.
        # Don't want to run an if statement for each data request
        try:
            return self._data
        except AttributeError:
            # When `self._data` doesn't exist. (caused by using `del ...`)
            if self._data_as_bytes is None:
                raise ValueError("Unable to restore data value from bytes when _data_as_bytes is None.")
            if self._model is not None:
                self.data = []
                for i in range(self.datatype.repeat):
                    sdict = SectionDict.from_model(self._model)
                    sdict.set_data_from_bytes(self._data_as_bytes[i])

                    self.data.append(sdict)
            else:
                self.set_data_from_bytes(self._data_as_bytes)
            return self.data

    @data.setter
    def data(self, value):
        if self.log_value:
            self._print_value_update(self._data, value)
        self._data = value

    @data.deleter
    def data(self):
        del self._data

    def setup_data_as_bytes(self, bytes_list, model=None) -> None:
        self._data_as_bytes = bytes_list
        self._model = model
        del self.data

    def get_data_as_bytes(self) -> bytes:
        self.update_datatype_repeat()

        if self.data is not None and self.datatype.repeat != 0:
            result = []
            if self.datatype.type == "struct":
                for struct in self.data:
                    result.append(struct.get_data_as_bytes())
            else:
                for value in listify(self.data):
                    result.append(parse_val_to_bytes(self, value))

            joined_result = b''.join(result)
        else:
            joined_result = b''

        if self.log_value:
            print(f"{self.to_simple_string()} (Data: {self.data}) retrieved: {joined_result}")

        return joined_result

    def set_data_from_byte_string(self, byte_string, start_from) -> None:
        necessary_bytes, _ = slice_bytes(self, byte_string, start_from)
        self.set_data_from_bytes(necessary_bytes)

    def set_data_from_bytes(self, bytes_list) -> None:
        if self.datatype.repeat > 0 and len(bytes_list) == 0:
            raise ValueError("Unable to set bytes when no bytes are given")
        if self.datatype.repeat > 0 and self.datatype.repeat != len(bytes_list):
            raise ValueError(f"Unable to set bytes when length of bytes list ({len(bytes_list)}) isn't equal to repeat ({self.datatype.repeat})")

        # print(f"bytes_list: {bytes_list}")

        result = [parse_bytes_to_val(self, entry_bytes) for entry_bytes in bytes_list]
        self.data = bytes_parser.vorl(self, result)

    def update_datatype_repeat(self) -> None:
        if type(self.data) == list:
            self.datatype.repeat = len(self.data)

    def set_data_to_default(self) -> None:
        if self.datatype.type == "data":
            data = bytes.fromhex(self.default_value)
        elif type(self.default_value) is list:
            data = self.default_value.copy()
            assert data is not self.default_value
        else:
            data = self.default_value

        self.data = data

    def duplicate(self):
        retriever = Retriever(
            name=self.name,
            default_value=self.default_value,
            datatype=self.datatype.duplicate(),
            is_list=self.is_list,
            log_value=self.log_value
        )
        for attr in attributes:
            if hasattr(self, attr):
                setattr(retriever, attr, getattr(self, attr))
        return retriever

    @classmethod
    def from_structure(cls, structure, name=None):
        if name is None and 'name' not in structure:
            raise ValueError("Parameter name is mandatory when not available in structure.")
        name = name or structure['name']

        datatype = DataType(var=structure.get('type'), repeat=structure.get('repeat', 1))
        retriever = cls(
            name=name,
            default_value=structure.get('default'),
            datatype=datatype,
            is_list=structure.get('is_list', None),
            log_value=structure.get('log', False)
        )

        # Go through dependencies if exist, else empty dict
        for dependency_name, properties in structure.get('dependencies', {}).items():
            if type(properties) is not list:
                r_dep = RetrieverDependency.from_structure(properties)
                _evaluate_is_list_attribute(retriever, r_dep)
                setattr(retriever, dependency_name, r_dep)
            else:
                dependency_list = []
                for dependency_struct in properties:
                    r_dep = RetrieverDependency.from_structure(dependency_struct)
                    _evaluate_is_list_attribute(retriever, r_dep)
                    dependency_list.append(r_dep)
                setattr(retriever, dependency_name, dependency_list)
        return retriever

    def _print_value_update(self, old, new) -> None:
        """
        Function to print when data is changed. Can also be called for when data is changed but the property doesn't
        fire. This happens when an array is adjusted in size by appending to it ([...] += [...]).

        Args:
            old (str): The old value represented using a string
            new (str): The new value represented using a string
        """
        print(f"{self.to_simple_string()} >>> set to: {string_manipulations.q_str(new)} "
              f"(was: {string_manipulations.q_str(old)})")

    def get_short_str(self):
        if self.data is not None:
            if type(self.data) is list:
                data = pretty_format_list(self.data)
            else:
                data = string_manipulations.q_str(self.data)
            return self.name + " (" + self.datatype.to_simple_string() + "): " + data
        else:
            return "<None>"

    def to_simple_string(self):
        return f"[Retriever] {self.name}: {self.datatype} (Default: {string_manipulations.q_str(self.default_value)})"

    def __repr__(self):
        if type(self.data) is list:
            data = str(pretty_format_list(self.data))
        else:
            data = self.data
            if len(str(data).splitlines()) > 1:
                data = f"\n{self.data}"
            data = string_manipulations.q_str(data)
        data = add_tabs(data, 1)
        # extra = []
        # for attr in attributes:
        #     if hasattr(self, attr):
        #         extra.append(f'\n{attr}: ' + str(getattr(self, attr)))
        return f"{self.to_simple_string()} >>> {data}"  # + string_manipulations.add_tabs(''.join(extra), 1)


def _evaluate_is_list_attribute(retriever, dependency):
    if dependency.dependency_action == DependencyAction.SET_REPEAT and retriever.is_list is None:
        retriever.is_list = True


attributes = ['on_refresh', 'on_construct', 'on_commit']
