from copy import copy


def numbers():
    yield from range(99999)


counter = numbers()
variable_retrievers = {}


def mark_retrievers(section):
    for name, retriever in section['retrievers'].items():
        retriever['id'] = next(counter)

        if retriever_is_variable(retriever):
            variable_retrievers[retriever['id']] = copy(retriever)
            variable_retrievers[retriever['id']]['name'] = name

        if retriever['type'][:7] == "struct:":
            rtype = retriever['type'][7:]
            mark_retrievers(section['structs'][rtype])


def retriever_is_variable(retriever):
    if retriever['type'][:3] == "str":
        return True
    if 'dependencies' in retriever:
        for key in retriever['dependencies']:
            if retriever['dependencies'][key]['action'] == "SET_REPEAT":
                return True
    return False
