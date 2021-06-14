def get_value(structure, path):
    for p in path:
        structure = structure[p]
        structure = into_retrievers(structure)
    return structure


def into_retrievers(structure):
    return structure['retrievers'] if 'retrievers' in structure else structure


# def func(structure, vrm, retriever):
#     vrm.get_value(retriever)


# def path_exists(structure, path):
#     return not not get_value(structure, path)
