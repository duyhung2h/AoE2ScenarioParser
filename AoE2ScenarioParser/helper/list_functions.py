from typing import List, Union


def hash_list(lst: List):
    return hash(tuple(lst))


def list_changed(lst, lst_hash):
    return lst_hash != hash(tuple(lst))


def listify(var) -> List:
    """Always return item as list"""
    if type(var) is list:
        return var
    else:
        return [var]


def update_order_array(order_array, supposed_length):
    for i in range(supposed_length):
        if i not in order_array:
            order_array.append(i)


def sum_len(iterable: List[Union[str, bytes]]) -> int:
    return sum(map(len, iterable))
