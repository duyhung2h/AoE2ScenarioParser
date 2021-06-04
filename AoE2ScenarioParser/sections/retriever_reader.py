def get_value(structure, path):
    for p in path:
        if 'retrievers' in structure:
            structure = structure['retrievers']
        structure = structure[p]
    return structure


def func(structure, vrm, retriever):
    vrm.get_value(retriever)


# def path_exists(structure, path):
#     return not not get_value(structure, path)
