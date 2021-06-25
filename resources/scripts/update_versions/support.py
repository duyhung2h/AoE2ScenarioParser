import copy
from typing import Dict, Optional

from AoE2ScenarioParser.sections.retrievers.datatype import datatype_to_type_length
from AoE2ScenarioParser.sections.sectiondict import SectionDict


def numbers():
    yield from range(99999)


section_dict_keys = dir(SectionDict())
counter = numbers()
dynamic_retrievers = {}


def mark_retrievers(path, section, return_result=False) -> Optional[Dict[str, Dict]]:
    child_retrievers = {}
    for name, retriever in section['retrievers'].items():
        validate_name(path, name)

        retriever['id'] = next(counter)
        rtype = retriever['type'][7:]

        if retriever_is_dynamic(retriever):
            rcopy = copy.copy(retriever)

            if not return_result:
                dynamic_retrievers[retriever['id']] = rcopy

            rcopy['name'] = name
            rcopy['path'] = path + [name]
            if retriever['type'][:7] == "struct:":
                struct = section['structs'][rtype]

                rcopy['has_dynamic_content'] = struct_content_is_dynamic(struct)
                rcopy['dynamic_children'] = mark_retrievers(path + [name + "[__index__]"], struct, True)
                rcopy['child_count'] = len(struct['retrievers'])
                rcopy['static_length'] = get_struct_length(struct)

            child_retrievers[rcopy['id']] = rcopy
    return child_retrievers


def validate_name(path, name):
    if name in section_dict_keys:
        p = ' -> '.join(path + [f"{name}"])
        space_len = len(p) - len(name) + 35  # 35 == Error msg length
        pointer = f"\n{' ' * space_len}{'^' * len(name)}"
        raise ValueError(f"Illegal name found in: {p}{pointer}")


def get_struct_length(struct) -> int:
    return sum(map(get_retriever_length, struct['retrievers'].values()))


def get_retriever_length(retriever) -> int:
    datatype, length = datatype_to_type_length(retriever['type'])
    return (length if datatype not in ['str', 'struct'] else 0) * retriever.get('repeat', 1)


def retriever_is_dynamic(retriever) -> bool:
    if retriever['type'][:3] == "str":
        return True
    if 'dependencies' in retriever:
        for key in retriever['dependencies']:
            if retriever['dependencies'][key]['action'] == "SET_REPEAT":
                return True
    return False


def struct_content_is_dynamic(struct) -> bool:
    return any(map(retriever_is_dynamic, struct['retrievers'].values()))
