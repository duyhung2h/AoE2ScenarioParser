import copy

from AoE2ScenarioParser.sections.retrievers.datatype import datatype_to_type_length
from AoE2ScenarioParser.sections.sectiondict import SectionDict


def numbers():
    yield from range(99999)


section_dict_keys = dir(SectionDict())
counter = numbers()
dynamic_retrievers = {}


def mark_retrievers(path, section):
    for name, retriever in section['retrievers'].items():
        validate_name(path, name)

        retriever['id'] = next(counter)

        if retriever_is_dynamic(retriever):
            dynamic_retrievers[retriever['id']] = rcopy = copy.copy(retriever)

            rcopy['name'] = name
            rcopy['path'] = path + [name]
            if retriever['type'][:7] == "struct:":
                rcopy['children'] = len(section['structs'][retriever['type'][7:]]['retrievers'])

        if retriever['type'][:7] == "struct:":
            rtype = retriever['type'][7:]
            struct = section['structs'][rtype]

            mark_retrievers(path + [name + "[__index__]"], struct)

            if not struct_content_is_dynamic(struct):
                retriever['static_length'] = get_struct_length(struct)


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
    return length if datatype not in ['str', 'struct'] else -1


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
