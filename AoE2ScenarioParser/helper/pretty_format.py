from typing import List, Dict

from AoE2ScenarioParser.helper.string_manipulations import create_inline_line, add_tabs

_default_inline_types = {
    'int': 8,
    'float': 8
}


def pretty_format_list(plist: List, inline_types: Dict[str, int] = None):
    if len(plist) == 0:
        return "[]"
    if inline_types is None:
        inline_types = _default_inline_types
    entry_type = type(plist[0]).__name__  # Get entry type

    return_string = "[\n"
    tabbed_string = ""
    line_items = []
    for index, entry in enumerate(plist):
        if entry_type in inline_types.keys():
            line_items.append(entry)
            if index % inline_types[entry_type] == inline_types[entry_type] - 1:
                tabbed_string += create_inline_line(line_items)
                line_items = []
            continue
        else:
            tabbed_string += f"{entry}\n"
    return_string += add_tabs(tabbed_string, 1)
    if len(line_items) != 0:
        return_string += create_inline_line(line_items)
    return return_string + "]"


def pretty_format_dict(pdict: dict):
    return_string = ""
    for key, value in pdict.items():
        newline = f"{key}: {value}"
        if newline[::-2] != "\n":
            newline += "\n"
        return_string += newline

    if return_string != "":
        return_string = "\n" + add_tabs(return_string, 1)

    return "{" + return_string + "}"


def pretty_format_name(name: str) -> str:
    """
    Returns a pretty-printed version of the name string.
    Replaces all underscores with spaces and capitalizes the first letter
    of each word.
    For example, elite_chu_ko_nu -> Elite Chu Ko Nu.

    :Author:
        T-West (https://github.com/twestura/)
    """
    return ' '.join(s.capitalize() for s in name.split('_'))
