from typing import TYPE_CHECKING

from AoE2ScenarioParser.helper.bytes_parser import retrieve_bytes
from AoE2ScenarioParser.helper.incremental_generator import IncrementalGenerator
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict
from AoE2ScenarioParser.objects.aoe2_object import AoE2Object
from AoE2ScenarioParser.sections.aoe2_file_section import AoE2FileSection
from AoE2ScenarioParser.sections.dependencies.dependency import handle_retriever_dependency
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever

if TYPE_CHECKING:
    from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario


class VariableRetrieverManager:
    def __init__(self, scenario_ref):
        self.scenario: AoE2DEScenario = scenario_ref
        self.variable_retrievers = None
        self.progress_id = -1

    def get_value(self, name, structure):
        retriever_id = int(structure['id'])

        print("\n\n>>> Getting value")
        print(f"Name:      {name}")
        print(f"Structure: {structure}")

        if self.progress_id > retriever_id:
            pass  # Needs a return

        for vr_id in self.variable_retrievers.keys():
            if self.progress_id < retriever_id and self.progress_id < int(vr_id):
                print("\n>>> Found unresolved retriever!")
                vr_structure = self.variable_retrievers[vr_id]
                print(f"Structure: {vr_structure}")
                bytes_until = self.get_length_until(int(vr_id))
                retriever = Retriever.from_structure(vr_structure, vr_structure['name'])

                # Todo: Find a way to have available the current parent SectionDict (?)
                # Todo: Truly no clue how to fix this...
                # Todo: Not even sure if it's possible without rewriting something huge...
                # Todo: Again, no idea what and how (yet (??)
                self_section_dict = AoE2FileSection('NAME', {})

                if hasattr(retriever, 'on_construct'):
                    handle_retriever_dependency(retriever, 'construct', self_section_dict, self.scenario.sections)

                # Todo: Shouldn't need Incremental generator to get the bytes
                necessary_bytes = retrieve_bytes(
                    IncrementalGenerator('_name_', self.scenario.decompressed_file, bytes_until), retriever
                )

                print(necessary_bytes)
                # print(retriever.set_data_from_bytes())
                # print(retriever)
                # print(vr_structure)
                # exit()

        print(retriever_id)
        exit()

    def get_length_until(self, rid):
        g = retriever_generator_from(self.scenario.structure, 0)
        total_length = 0
        for _ in range(rid):
            retriever = next(g)
            if str(retriever['id']) in self.variable_retrievers:
                return
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
