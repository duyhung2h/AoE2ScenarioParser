import copy

from AoE2ScenarioParser.sections.retrievers.datatype import datatype_to_type_length


def numbers():
    yield from range(99999)


counter = numbers()
dynamic_retrievers = {}


def mark_retrievers(path, section):
    for name, retriever in section['retrievers'].items():
        retriever['id'] = next(counter)
        # retriever['length'] = get_retriever_length(retriever)

        # try:
        #     del retriever['length']
        # except KeyError:
        #     pass

        if retriever_is_dynamic(retriever):
            dynamic_retrievers[retriever['id']] = copy.copy(retriever)
            rcopy = dynamic_retrievers[retriever['id']]

            rcopy['name'] = name
            rcopy['path'] = path + [name]

        if retriever['type'][:7] == "struct:":
            rtype = retriever['type'][7:]
            mark_retrievers(path + [name + "[__index__]"], section['structs'][rtype])

            struct = section['structs'][retriever['type'][7:]]
            if not struct_content_is_dynamic(struct):
                retriever['static_length'] = get_struct_length(struct)


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
