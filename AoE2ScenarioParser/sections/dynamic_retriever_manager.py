from pathlib import Path
from turtledemo.penrose import draw
from typing import TYPE_CHECKING, Generator, List, Dict, Tuple

from AoE2ScenarioParser.helper.bytes_parser import slice_bytes
from AoE2ScenarioParser.helper.exceptions import TargetRetrieverReached
from AoE2ScenarioParser.helper.list_functions import sum_len
from AoE2ScenarioParser.helper.pretty_format import pretty_format_list, pretty_format_dict
from AoE2ScenarioParser.helper.printers import rprint
from AoE2ScenarioParser.helper.string_manipulations import split_string_blocks, create_textual_hex, add_tabs, q_str
from AoE2ScenarioParser.sections.aoe2_struct_model import AoE2StructModel
from AoE2ScenarioParser.sections.dependencies.dependency import handle_retriever_dependency
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever
from AoE2ScenarioParser.sections.sectiondict import SectionDict

if TYPE_CHECKING:
    from AoE2ScenarioParser.scenarios.aoe2_scenario import AoE2Scenario


def resolve_struct_path(structure, path):
    path = [p.replace('[__index__]', '') for p in path]
    print(f"\n\nPath: {path}")

    current_structure = structure
    for index, p in enumerate(path):
        print("\n")
        print(f"{p in structure.keys()} \t|| {structure}")
        print(f"{p in current_structure.keys()} \t|| {current_structure}")
        print(f"current_structure[{p}] -?-> 'retrievers'...")

        current_structure = into_retrievers(current_structure[p])

        if 'type' in current_structure and type_is_struct(current_structure):
            print(">>> TYPE IS STRUCT")
            struct_name = get_struct_name(current_structure)
            print(f"struct_name: {struct_name}")
            print("Structure keys:")
            print(f"\t{structure.keys()}")
            parent_path = path[index - 1]
            print(f"Parent p: {parent_path}")
            print(f"structure[{parent_path}] --> {parent_path in structure.keys()}")
            structure = parent = structure[parent_path]['structs']
            current_structure = parent[struct_name]
            path[index] = struct_name  # Change path struct name
            print(f">>> NEW PATH: {path}")  # Todo: Might be a cleaner way to fix this

        if index != len(path) - 1:
            current_structure = into_retrievers(current_structure)

    print(f"Returning: {current_structure}")
    return current_structure


def resolve_path(structure, path, end_in_retrievers=True):
    # print(path)
    try:
        for index, p in enumerate(path):
            # print(p)
            # print(structure.keys())
            if '[__index__]' in p:
                p = p.replace('[__index__]', '')
            structure = structure[p]

            if end_in_retrievers or index != len(path) - 1:
                structure = into_retrievers(structure)
        return structure
    except KeyError:
        raise KeyError(f"Path '{'->'.join(path)}' cannot be found.")


def into_retrievers(structure):
    return structure['retrievers'] if 'retrievers' in structure else structure


def get_struct_retrievers(structure, struct_retriever):
    struct_name = get_struct_name(struct_retriever)
    parent = resolve_path(structure, struct_retriever['path'][:-1], end_in_retrievers=False)

    return parent['structs'][struct_name]['retrievers']


class ContinueDiscover(Exception):
    pass


class DynamicRetrieverManager:
    def __init__(self):
        # Debugging mode
        self.debug_mode = True
        self.debug_store: Dict[int, Tuple[int, int, 'Retriever']] = {}  # { byte_loc : (length, rid, retr) }

        self.scenario = None
        self.dynamic_retrievers = None
        self.dynamic_int_keys: List[int] = []
        self.dynamic_child_parent_map: Dict[str, List[str]] = {}
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

            # Create child-parent map. Result: { 'child_id': ['parent_id', 'parents_parent_id' ...], ... }
            def handle_dynamic_children(structure, parent_path):
                for key, child_structure in structure.items():
                    self.dynamic_child_parent_map.setdefault(str(child_structure['id']), []).extend(parent_path)

                    if 'dynamic_children' in child_structure:
                        handle_dynamic_children(child_structure['dynamic_children'], parent_path + [str(key)])

            handle_dynamic_children(value, [])

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
                except KeyError:
                    dlength = -1

                f.write(f"{unparsed_bytes_before}")
                f.write(f"\n\n[ID: {rid}, DL, L: {dlength}, {length}] {retr}\n\n{own_bytes}\n\n")
                last_byte_loc = byte_loc + length

            f.write(create_textual_hex(dc_file[last_byte_loc:].hex()))
        rprint("Writing debug file finished successfully!", final=True)

    def register_debug_entry(self, retriever, retriever_id, length_until, sum_necessary_bytes):
        if self.debug_mode:
            self.debug_store[length_until] = (sum_necessary_bytes, retriever_id, retriever)

    def discover_until(self, until_rid: int, dynamic_int_keys: List[int]):
        dynamic_int_keys = [x for x in dynamic_int_keys if self.progress_id < x <= until_rid]
        print(f"discover until: {until_rid}. To resolve: {dynamic_int_keys}")
        print(f"Current progress: {self.progress_id}")

        if not dynamic_int_keys:
            print(f">>> Skip all [Progress ID >= (discover Until ID || Last Dynamic Int Key)]")
            return

        for dynamic_retriever_id in dynamic_int_keys:
            if self.progress_id >= dynamic_retriever_id:
                print(f"\t[{dynamic_retriever_id}]  \tContinue")
                continue  # Going to parse already parsed retriever. Next.
            elif dynamic_retriever_id > until_rid:
                print(f"\t[{dynamic_retriever_id}]  \tReturn")
                return  # Going to parse further than requested. Cancel.
            elif self.progress_id < until_rid:
                print(f"\n\t[{dynamic_retriever_id}]  \tProgressing... <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                drs = self.dynamic_retrievers[str(dynamic_retriever_id)]  # drs = Dynamic Retriever Structure
                retriever = Retriever.from_structure(drs, drs['name'])
                length_until = self.get_number_of_bytes_before(dynamic_retriever_id)

                handle_retriever_dependency(
                    retriever, 'construct',
                    self.scenario.sections[drs['path'][0]],  # Todo: Add support within struct and nested etc.
                    self.scenario.sections
                )

                if retriever.datatype.repeat == 0:  # Skip parsing when repeat is 0
                    retriever.data = []
                    self._handle_parsed_retriever(retriever, drs, length_until, 0)
                    continue

                if type_is_struct(drs):
                    try:
                        self._handle_struct_discover(drs, retriever, length_until)
                    except ContinueDiscover:
                        continue
                else:
                    necessary_bytes, _ = slice_bytes(retriever, self.scenario.file_content, length_until)

                    retriever.setup_data_as_bytes(necessary_bytes)
                    self._handle_parsed_retriever(
                        retriever=retriever,
                        dynamic_retriever_structure=drs,
                        length_until=length_until,
                        length=sum_len(necessary_bytes),
                        register_as_progress=True
                    )
                    if until_rid == dynamic_retriever_id:
                        return retriever

    def _handle_struct_discover(self, drs, retriever, progress, parent_index=None):
        if parent_index is None:
            parent_index = []
        initial_progress = progress
        struct_name = get_struct_name(drs)
        static_length, struct_has_dynamic_content = drs['static_length'], drs['has_dynamic_content']

        if struct_has_dynamic_content:
            before_dict = get_length_before_dynamic_retrievers(
                drs['dynamic_children'].keys(), get_struct_retrievers(self.structure, drs)
            )

            retriever_data = []
            for i in range(retriever.datatype.repeat):
                retriever_data.append(SectionDict(drm=self, index=i))

                # { rid : retriever_structure } -> Dict[str, Dict]
                for rid, retriever_structure in drs['dynamic_children'].items():
                    retriever_name = retriever_structure['name']
                    skip = before_dict[int(rid)]

                    child_retriever = Retriever.from_structure(retriever_structure, retriever_name)

                    print(f"Name: \t{retriever_structure['name']}")

                    if type_is_struct(retriever_structure):
                        self._handle_struct_discover(retriever_structure, child_retriever, progress)

                    necessary_bytes, _ = slice_bytes(child_retriever, self.scenario.file_content, progress + skip)
                    child_retriever.setup_data_as_bytes(necessary_bytes)

                    retriever_data[i][retriever_name] = child_retriever

                    progress += skip + sum_len(necessary_bytes)

            retriever.data = retriever_data
            self._handle_parsed_retriever(
                retriever=retriever,
                dynamic_retriever_structure=drs,
                length_until=initial_progress,
                length=progress - initial_progress
            )
            raise ContinueDiscover("Continue outer function loop")
        else:
            total_static_length = retriever.datatype.repeat * static_length
            byte_string = self.scenario.file_content[progress:progress + total_static_length]
            necessary_bytes = split_string_blocks(byte_string, static_length)

            model_structure = resolve_struct_path(self.structure, drs['path'])

            print(f"Model: {model_structure}")

            # Todo: Do I really need models?  -- I probably do.
            model = AoE2StructModel.from_structure(struct_name, model_structure, self)
            model.parent_path = drs['path']

        # print(f"necessary_bytes: {necessary_bytes}")

        retriever.setup_data_as_bytes(necessary_bytes, model)
        self._handle_parsed_retriever(
            retriever=retriever,
            dynamic_retriever_structure=drs,
            length_until=initial_progress,
            length=sum_len(necessary_bytes),
            register_as_progress=True
        )

    def determine_value(self, path):
        print(f">>> Get value function called. Path: {path}")

        retriever_structure = resolve_path(self.structure, path)
        retriever_id = int(retriever_structure['id'])
        name = path[-1]

        print("\n\n>>> Getting value")
        print(f"Name:      {name}")
        print(f"Structure: {retriever_structure}")

        # if self.progress_id > retriever_id:
        #     pass  # Needs a return

        self.discover_until(retriever_id, self.dynamic_int_keys)
        # if dynamic_retriever_id > retriever_id:

        # Solve requested retriever
        length_until = self.get_number_of_bytes_before(retriever_id)

        print(f"length_until: {length_until}")

        retriever = Retriever.from_structure(retriever_structure, name)
        # retriever = resolve_path(self.structure, path)

        print(f"retriever_id: {q_str(retriever_id)}")

        if retriever_id in self.dynamic_int_keys:
            print(self.scenario.sections['Units'].keys())
            exit(99)
            retriever = self.scenario.get_retriever(path)
            print(f"RETURNING! {retriever.to_simple_string()}")
            return retriever
 
        necessary_bytes, _ = slice_bytes(retriever, self.scenario.file_content, length_until)
        print(f"necessary_bytes: {q_str(necessary_bytes[0])}")
        retriever.set_data_from_bytes(necessary_bytes)

        self.register_debug_entry(retriever, retriever_id, length_until, sum_len(necessary_bytes))
        self.progress_id = retriever_id

        print(f"\n>>> RESULT: {retriever.to_simple_string()}\n\n")
        return retriever

        # for dynamic_retriever_id in self.dynamic_int_keys:
        #
        #     elif self.progress_id < retriever_id and self.progress_id < dynamic_retriever_id:
        #         # Solve in-between unresolved retrievers
        #         dr_structure = self.dynamic_retrievers[str(dynamic_retriever_id)]
        #
        #         length_until = self.get_number_of_bytes_before(dynamic_retriever_id)
        #         retriever = Retriever.from_structure(dr_structure, dr_structure['name'])
        #
        #         handle_retriever_dependency(
        #             retriever, 'construct',
        #             self.scenario.sections[dr_structure['path'][0]],
        #             self.scenario.sections
        #         )
        #
        #         if retriever.datatype.repeat == 0:  # Skip parsing when repeat is 0
        #             retriever.data = []
        #             self._handle_parsed_retriever(
        #                 retriever=retriever,
        #                 dynamic_retriever_structure=dr_structure,
        #                 length_until=length_until,
        #                 length=0
        #             )
        #             continue
        #
        #         necessary_bytes = []
        #         model = None
        #         if type_is_struct(dr_structure):
        #             struct_name = get_struct_name(dr_structure)
        #             static_length = dr_structure['static_length']
        #             has_dynamic_content = dr_structure['has_dynamic_content']
        #
        #             if has_dynamic_content:
        #                 before_dict = get_length_before_dynamic_retrievers(
        #                     dr_structure['dynamic_children'].keys(),
        #                     get_struct_retrievers(self.structure, dr_structure)
        #                 )
        #
        #                 progress = length_until
        #                 child_retriever_result = []
        #                 for i in range(retriever.datatype.repeat):
        #                     child_retriever_result.append(SectionDict(drm=self, index=i))
        #
        #                     # { rid : child_retriever } -> Dict[str, Dict]
        #                     for rid, retriever_structure in dr_structure['dynamic_children'].items():
        #                         retriever_name = retriever_structure['name']
        #                         skip = before_dict[int(rid)]
        #
        #                         child_retriever = Retriever.from_structure(retriever_structure, retriever_name)
        #                         necessary_bytes, _ = slice_bytes(child_retriever, self.scenario.file_content,
        #                                                          progress + skip)
        #                         child_retriever.setup_data_as_bytes(necessary_bytes)
        #
        #                         child_retriever_result[i][retriever_name] = child_retriever
        #
        #                         progress += skip + sum_len(necessary_bytes)
        #
        #                 retriever.data = child_retriever_result
        #                 self._handle_parsed_retriever(
        #                     retriever=retriever,
        #                     dynamic_retriever_structure=dr_structure,
        #                     length_until=length_until,
        #                     length=progress - length_until
        #                 )
        #                 continue
        #
        #             else:
        #                 total_static_length = retriever.datatype.repeat * static_length
        #                 byte_string = self.scenario.file_content[length_until:length_until + total_static_length]
        #                 necessary_bytes = split_string_blocks(byte_string, static_length)
        #
        #                 parent_path = dr_structure['path'][:-1]
        #                 section_structure = resolve_path(self.structure, parent_path, end_in_retrievers=False)
        #
        #                 # Todo: Do I really need models?
        #                 model = model_dict_from_structure(section_structure, self)[struct_name]
        #                 model.parent_path = parent_path
        #         else:
        #             necessary_bytes, _ = slice_bytes(retriever, self.scenario.file_content, length_until)
        #
        #         retriever.setup_data_as_bytes(necessary_bytes, model)
        #         self._handle_parsed_retriever(
        #             retriever=retriever,
        #             dynamic_retriever_structure=dr_structure,
        #             length_until=length_until,
        #             length=sum_len(necessary_bytes),
        #             register_as_progress=True
        #         )
        #         if retriever_id == dynamic_retriever_id:
        #             return retriever

    def _handle_parsed_retriever(self, retriever, dynamic_retriever_structure, length_until, length,
                                 register_as_progress=False):
        dynamic_retriever_id = dynamic_retriever_structure['id']

        if register_as_progress:
            self.progress_id = dynamic_retriever_id

        self._set_dynamic_retriever_length(dynamic_retriever_id, length)
        self._register_retriever_in_section(dynamic_retriever_structure, retriever)
        self.register_debug_entry(retriever, dynamic_retriever_id, length_until, length)

    def _register_retriever_in_section(self, dynamic_retriever_structure, retriever) -> None:
        parent_path = dynamic_retriever_structure['path'][:-1]
        self.scenario.get_retriever(parent_path)[retriever.name] = retriever

    def _get_dynamic_retriever(self, dr_id: str):
        if dr_id not in self.dynamic_child_parent_map.keys():
            raise ValueError("Dynamic child ID doesn't exist.")

        parent_id_path = self.dynamic_child_parent_map[dr_id]
        if not parent_id_path:
            return self.dynamic_retrievers[dr_id]

        drs = {}
        for index, parent_id in enumerate(parent_id_path):
            drs = self.dynamic_retrievers[parent_id]

            if index != len(parent_id_path):
                drs = drs['dynamic_children']
        return drs

    def _set_dynamic_retriever_length(self, dr_id, length) -> None:
        self._get_dynamic_retriever(str(dr_id))['length'] = length

    def get_number_of_bytes_before(self, rid: int) -> int:
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
                # print(f"L1: {current_len} ({string_id})")
            else:
                current_len = get_static_retriever_length(retriever) * retriever.get('repeat', 1)
                # print(f"L2: {current_len} ({string_id})")
            total_length += current_len

        # print(f"Before: {total_length}")
        return total_length


def get_struct_name(retriever: dict) -> str:
    if 'struct:' not in retriever['type']:
        raise ValueError("Retriever is not a struct.")
    return retriever['type'][7:]


def type_is_struct(retriever_structure: dict) -> bool:
    return retriever_structure['type'][:7] == "struct:"


# Todo: Horrible naming. Bytes between dynamics
def get_length_before_dynamic_retrievers(dynamic_ids: List[int], retrievers: Dict[str, dict]) -> Dict[int, int]:
    length_before = {}

    length_encountered = 0
    for name, retriever in retrievers.items():
        if str(retriever['id']) in dynamic_ids:
            length_before[retriever['id']] = length_encountered
            length_encountered = 0
        else:
            length_encountered += get_static_retriever_length(retriever)

    return length_before


def get_static_retriever_length(retriever_structure: dict) -> int:
    # Filter numbers out for length, filter text for type
    var_len = int(''.join(filter(str.isnumeric, retriever_structure['type'])))
    var_type = ''.join(filter(str.isalpha, retriever_structure['type']))

    if var_type == '':
        var_type = "data"

    # Divide by 8, and parse from float to int
    if var_type not in ["c", "data"]:
        var_len = int(var_len / 8)

    return var_len


def retriever_generator(structure: dict, from_retriever_id: int, until_retriever_id: int = -1) -> Generator:
    def loop(s):
        for retriever in s['retrievers'].values():
            if retriever['id'] >= until_retriever_id != -1:
                raise TargetRetrieverReached('Reached until retriever id')
            if type_is_struct(retriever):
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
