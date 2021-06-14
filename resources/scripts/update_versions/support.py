import copy


def numbers():
    yield from range(99999)


counter = numbers()
dynamic_retrievers = {}


def mark_retrievers(path, section):
    for name, retriever in section['retrievers'].items():
        retriever['id'] = next(counter)

        if retriever_is_variable(retriever):
            dynamic_retrievers[retriever['id']] = copy.copy(retriever)
            dynamic_retrievers[retriever['id']]['name'] = name
            dynamic_retrievers[retriever['id']]['path'] = path + [name]

        if retriever['type'][:7] == "struct:":
            rtype = retriever['type'][7:]
            mark_retrievers(path + [name + "[__index__]"], section['structs'][rtype])


def retriever_is_variable(retriever):
    if retriever['type'][:3] == "str":
        return True
    if 'dependencies' in retriever:
        for key in retriever['dependencies']:
            if retriever['dependencies'][key]['action'] == "SET_REPEAT":
                return True
    return False
