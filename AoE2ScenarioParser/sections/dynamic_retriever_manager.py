from pathlib import Path
from pathlib import Path
from typing import TYPE_CHECKING

from AoE2ScenarioParser.helper.bytes_parser import slice_bytes
from AoE2ScenarioParser.helper.exceptions import TargetRetrieverReached
from AoE2ScenarioParser.helper.list_functions import sum_len
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list
from AoE2ScenarioParser.helper.printers import rprint
from AoE2ScenarioParser.helper.string_manipulations import split_string_blocks, create_textual_hex, add_tabs
from AoE2ScenarioParser.sections.aoe2_struct_model import model_dict_from_structure
from AoE2ScenarioParser.sections.dependencies.dependency import handle_retriever_dependency
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever
from AoE2ScenarioParser.sections.sectiondict import SectionDict

if TYPE_CHECKING:
    from AoE2ScenarioParser.scenarios.aoe2_scenario import AoE2Scenario


def resolve_path(structure, path, end_in_retrievers=True):
    try:
        for index, p in enumerate(path):
            structure = structure[p]

            if end_in_retrievers or index != len(path) - 1:
                structure = into_retrievers(structure)
        return structure
    except KeyError:
        raise KeyError(f"Path '{'->'.join(path)}' cannot be found.") from None


def get_struct_retrievers(structure, struct_retriever):
    struct_name = get_struct_name(struct_retriever)
    parent = resolve_path(structure, struct_retriever['path'][:-1], False)

    return parent['structs'][struct_name]['retrievers']


def into_retrievers(structure):
    return structure['retrievers'] if 'retrievers' in structure else structure


class DynamicRetrieverManager:
    def __init__(self):
        # Debugging mode
        self.debug_mode = True
        self.debug_store = {}

        self.scenario = None
        self.dynamic_retrievers = None
        self.dynamic_int_keys = []
        self.progress_id = -1

    @property
    def scenario(self) -> 'AoE2Scenario':
        return self._scenario

    @scenario.setter
    def scenario(self, value):
        self._scenario = value

    @property
    def structure(self):
        if self.scenario is not None:
            return self.scenario.structure
        else:
            raise ValueError("Scenario hasn't been injected. Structure not available")

    @property
    def dynamic_retrievers(self) -> dict[str, dict]:
        return self._dynamic_retrievers

    @dynamic_retrievers.setter
    def dynamic_retrievers(self, value: dict[str, dict]):
        self._dynamic_retrievers = value
        if type(value) is dict:
            self.dynamic_int_keys = list(map(int, value.keys()))

    def _write_debug_file(self):
        rprint("\nWriting debug file...")
        with open(Path(__file__).parent.parent / 'debug_file.txt', 'w') as f:
            dc_file = self.scenario.decompressed_file

            print(self._dynamic_retrievers.keys())
            print(pretty_format_list(list(map(lambda r: r[1], self.debug_store.values()))))

            last_byte_loc = 0
            for byte_loc, (length, rid, retr) in sorted(self.debug_store.items()):

                unparsed_bytes_before = create_textual_hex(dc_file[last_byte_loc:byte_loc].hex())
                own_bytes = add_tabs(create_textual_hex(dc_file[byte_loc:byte_loc + length].hex()), 2)
                own_bytes += " (own)" if own_bytes.strip() != "" else "<<EMPTY>>"
                try:
                    dlength = self._dynamic_retrievers[str(rid)]['length']
                except KeyError as e:
                    dlength = -1

                f.write(f"{unparsed_bytes_before}")
                f.write(f"\n\n[ID: {rid}, DL, L: {dlength}, {length}] {retr}\n\n{own_bytes}\n\n")
                last_byte_loc = byte_loc + length

            f.write(create_textual_hex(dc_file[last_byte_loc:].hex()))
        rprint("Writing debug file finished successfully!", final=True)

    def register_debug_entry(self, retriever, retriever_id, bytes_until, sum_necessary_bytes):
        if self.debug_mode:
            self.debug_store[bytes_until] = (sum_necessary_bytes, retriever_id, retriever)

    # Todo: Split getting value and discovering until into different functions
    def determine_value(self, path):
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
                # Solve requested retriever
                bytes_until = self.get_length_until(retriever_id)
                retriever = Retriever.from_structure(retriever_structure, name)

                necessary_bytes, _ = slice_bytes(retriever, self.scenario.file_content, bytes_until)
                retriever.set_data_from_bytes(necessary_bytes)

                self.register_debug_entry(retriever, retriever_id, bytes_until, sum_len(necessary_bytes))
                return retriever

            elif self.progress_id < retriever_id and self.progress_id < dynamic_retriever_id:
                # Solve in-between unresolved retrievers
                dr_structure = self.dynamic_retrievers[str(dynamic_retriever_id)]

                bytes_until = self.get_length_until(dynamic_retriever_id)
                retriever = Retriever.from_structure(dr_structure, dr_structure['name'])

                # Clean up and add recursion for nested structs 
                if hasattr(retriever, 'on_construct'):
                    handle_retriever_dependency(
                        retriever,
                        'construct',
                        self.scenario.sections[dr_structure['path'][0]],
                        self.scenario.sections
                    )

                if retriever.datatype.repeat == 0:  # Skip parsing when repeat is 0
                    retriever.data = []
                    self.dynamic_retrievers[str(dynamic_retriever_id)]['length'] = 0
                    self.scenario.get_retriever(dr_structure['path'][:-1])[retriever.name] = retriever

                    self.register_debug_entry(retriever, dynamic_retriever_id, bytes_until, 0)
                    print(f"Skipped due to repeat = {retriever.datatype.repeat}")
                    print(">>> End of unresolved Structure")
                    continue

                necessary_bytes = []
                model = None
                if dr_structure['type'][:7] == "struct:":
                    static_length = dr_structure['static_length']
                    has_dynamic_content = dr_structure['has_dynamic_content']
                    struct_name = get_struct_name(dr_structure)

                    if has_dynamic_content:
                        before_dict = get_length_before_dynamic_retrievers(
                            dr_structure['dynamic_children'].keys(),
                            get_struct_retrievers(self.structure, dr_structure)
                        )

                        progress = bytes_until
                        child_retriever_result = []
                        for i in range(retriever.datatype.repeat):
                            child_retriever_result.append(SectionDict(drm=self, index=i))

                            # { rid : child_retriever } -> Dict[str, Dict]
                            for rid, retriever_structure in dr_structure['dynamic_children'].items():
                                rname = retriever_structure['name']
                                skip = before_dict[int(rid)]

                                child_retriever = Retriever.from_structure(retriever_structure, rname)
                                necessary_bytes, _ = slice_bytes(child_retriever, self.scenario.file_content, progress + skip)
                                child_retriever.setup_data_as_bytes(necessary_bytes)

                                child_retriever_result[i][rname] = child_retriever

                                progress += skip + sum_len(necessary_bytes)

                        retriever.data = child_retriever_result

                        self.dynamic_retrievers[str(dynamic_retriever_id)]['length'] = progress - bytes_until

                        self.scenario.get_retriever(dr_structure['path'][:-1])[retriever.name] = retriever

                        self.register_debug_entry(retriever, dynamic_retriever_id, bytes_until, progress - bytes_until)
                        continue

                    else:
                        total_static_length = retriever.datatype.repeat * static_length
                        byte_string = self.scenario.file_content[bytes_until:bytes_until + total_static_length]
                        necessary_bytes = split_string_blocks(byte_string, static_length)

                        parent_path = dr_structure['path'][:-1]
                        section_structure = resolve_path(self.structure, parent_path, end_in_retrievers=False)

                        # Do I really need models?
                        model = model_dict_from_structure(section_structure, self)[struct_name]
                        model.parent_path = parent_path
                else:
                    necessary_bytes, _ = slice_bytes(retriever, self.scenario.file_content, bytes_until)

                retriever.setup_data_as_bytes(necessary_bytes, model)
                self.dynamic_retrievers[str(dynamic_retriever_id)]['length'] = sum_len(necessary_bytes)
                # print(f"[Dynamic] Bytes: {necessary_bytes}")
                print("Result:")
                print(retriever.to_simple_string())
                self.progress_id = dynamic_retriever_id

                print(resolve_path(self.structure, dr_structure['path']))
                self.scenario.get_retriever(dr_structure['path'][:-1])[retriever.name] = retriever
                self.register_debug_entry(retriever, dynamic_retriever_id, bytes_until, sum_len(necessary_bytes))
                print(">>> End Getting Value")
                if retriever_id == dynamic_retriever_id:
                    return retriever

    def get_length_until(self, rid):
        total_length = ignore_count = 0
        retriever: dict
        for retriever in retriever_generator(self.scenario.structure, 0, rid):
            if ignore_count > 0:
                ignore_count -= 1
                continue

            string_id = str(retriever['id'])

            if string_id in self.dynamic_retrievers.keys():
                ignore_count = self.dynamic_retrievers[string_id].get('child_count', 0)
                current_len = self.dynamic_retrievers[string_id].get('length')
            else:
                current_len = get_static_retriever_length(retriever) * retriever.get('repeat', 1)
            total_length += current_len
        return total_length


def get_struct_name(retriever):
    if 'struct:' not in retriever['type']:
        raise ValueError("Retriever is not a struct.")
    return retriever['type'][7:]


def get_length_before_dynamic_retrievers(dynamic_ids, retrievers):
    length_before = {}

    length_encountered = 0
    for name, retriever in retrievers.items():
        if str(retriever['id']) in dynamic_ids:
            length_before[retriever['id']] = length_encountered
            length_encountered = 0
        else:
            length_encountered += get_static_retriever_length(retriever)

    return length_before


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


def retriever_generator(structure, from_retriever_id, until_retriever_id=-1):
    def loop(s):
        for retriever in s['retrievers'].values():
            if retriever['id'] >= until_retriever_id != -1:
                raise TargetRetrieverReached('Reached until retriever id')
            if retriever['type'][:7] == "struct:":
                yield retriever

                rtype = get_struct_name(retriever)
                yield from loop(s['structs'][rtype])
            else:
                if from_retriever_id <= int(retriever['id']):
                    yield retriever

    for section in structure.values():
        try:
            yield from loop(section)
        except TargetRetrieverReached:
            return
    yield None
