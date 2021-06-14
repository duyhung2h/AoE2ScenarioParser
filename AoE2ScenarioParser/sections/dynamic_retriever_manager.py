from typing import TYPE_CHECKING

from AoE2ScenarioParser.helper.bytes_parser import retrieve_bytes
from AoE2ScenarioParser.helper.incremental_generator import IncrementalGenerator
from AoE2ScenarioParser.helper.list_functions import sum_len
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict
from AoE2ScenarioParser.sections.aoe2_file_section import AoE2FileSection
from AoE2ScenarioParser.sections.dependencies.dependency import handle_retriever_dependency
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever

if TYPE_CHECKING:
    from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario


def resolve_path(structure, path):
    try:
        for p in path:
            structure = structure[p]
            structure = into_retrievers(structure)
        return structure
    except KeyError:
        raise KeyError(f"Path {path} cannot be found.") from None


def into_retrievers(structure):
    return structure['retrievers'] if 'retrievers' in structure else structure


class DynamicRetrieverManager:
    def __init__(self, scenario_ref):
        self.scenario: AoE2DEScenario = scenario_ref
        self.structure = scenario_ref.structure  # Ease of access

        self.dynamic_retrievers = None
        self.dynamic_int_keys = []
        self.progress_id = -1

    @property
    def dynamic_retrievers(self) -> dict[str, dict]:
        return self._dynamic_retrievers

    @dynamic_retrievers.setter
    def dynamic_retrievers(self, value: dict[str, dict]):
        self._dynamic_retrievers = value
        if type(value) is dict:
            self.dynamic_int_keys = list(map(int, value.keys()))

    def determine_value(self, path, host: AoE2FileSection):
        print(f">>> Get value function called. Path: {path}")

        retriever_structure = resolve_path(self.structure, path)
        retriever_id = int(retriever_structure['id'])
        name = path[-1]

        print("\n\n>>> Getting value")
        print(f"Name:      {name}")
        print(f"Structure: {retriever_structure}")

        if self.progress_id > retriever_id:
            pass  # Needs a return

        for dynamic_retriever_id in self.dynamic_int_keys:
            if dynamic_retriever_id > retriever_id:
                bytes_until = self.get_length_until(retriever_id)
                retriever = Retriever.from_structure(retriever_structure, name)

                # Todo: Shouldn't need Incremental generator to get the bytes
                necessary_bytes = retrieve_bytes(
                    IncrementalGenerator('_name_', self.scenario.decompressed_file, bytes_until), retriever
                )
                retriever.set_data_from_bytes(necessary_bytes)  # Todo: No need to parse this :)
                host.retriever_map[name] = retriever
                print(f"Bytes: {necessary_bytes}")
                print("Result:")
                print(f"{retriever}\n")
                return retriever

            elif self.progress_id < retriever_id and self.progress_id < dynamic_retriever_id:
                print("\n>>> Found unresolved retriever!")
                dr_structure = self.dynamic_retrievers[str(dynamic_retriever_id)]
                print(f"Unresolved Structure: {dr_structure['name']} -> {dr_structure}")
                bytes_until = self.get_length_until(dynamic_retriever_id)
                retriever = Retriever.from_structure(dr_structure, dr_structure['name'])

                if hasattr(retriever, 'on_construct'):
                    handle_retriever_dependency(
                        retriever,
                        'construct',
                        self.scenario.sections[dr_structure['path'][0]],
                        self.scenario.sections
                    )

                # Todo: Shouldn't need Incremental generator to get the bytes
                necessary_bytes = retrieve_bytes(
                    IncrementalGenerator('_name_', self.scenario.decompressed_file, bytes_until),
                    retriever
                )
                retriever.set_data_from_bytes(necessary_bytes)  # Todo: No need to parse this :)
                self.dynamic_retrievers[str(dynamic_retriever_id)]['length'] = sum_len(necessary_bytes)
                print(f"Bytes: {necessary_bytes}")
                print("Result:")
                print(retriever)
                self.progress_id = dynamic_retriever_id

    def get_length_until(self, rid):
        g = retriever_generator_from(self.scenario.structure, 0)
        total_length = 0
        for _ in range(rid):
            retriever = next(g)
            string_id = str(retriever['id'])

            if string_id in self.dynamic_retrievers:
                total_length += self.dynamic_retrievers[string_id]['length']
            else:
                total_length += get_static_retriever_length(retriever)
        return total_length


def get_static_retriever_length(retriever):
    # Filter numbers out for length, filter text for type
    var_len = int(''.join(filter(str.isnumeric, retriever['type'])))
    var_type = ''.join(filter(str.isalpha, retriever['type']))

    if var_type == '':
        var_type = "data"

    # Divide by 8, and parse from float to int
    if var_type not in ["c", "data"]:
        var_len = int(var_len / 8)

    return var_len


def retriever_generator_from(structure, rid):
    def loop(s):
        for retriever in s['retrievers'].values():
            if retriever['type'][:7] == "struct:":
                rtype = retriever['type'][7:]
                loop(s['structs'][rtype])
            else:
                if rid <= int(retriever['id']):
                    yield retriever

    for section in structure.values():
        gen = loop(section)
        while True:
            try:
                yield next(gen)
            except StopIteration:
                break
    yield None
