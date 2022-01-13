import json
import operator
import os
import sys
from functools import reduce
from pathlib import Path

import regex


def c_print(*args, colour: str = "white", **kwargs):
    """
    print() but with an option to specify a colour

    :param args: args to pass to print
    :param str colour: Normal
    :param kwargs: kwargs to pass to print
    """
    _colour = {
        'end': '\033[0m',
        'black': '\033[30m',
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
    }

    string = _colour[colour] + ' '.join(map(str, args)) + _colour["end"]
    print(string, **kwargs)


class PyInfoGenerator:
    """
    Generate information about all python files in a folder, such as the classes, their methods, attributes, etc. as
    json files (which could then be used to make documentation) for all python files within a folder and its sub folders
    """

    def __init__(self, folder_name: str):
        """
        :param str folder_name: The folder to scan for python files and generate information for
        """
        self.ignored_dirs = [".git", ".idea", "venv", ".vscode"]
        self.ignored_files = []
        self.folder_name = folder_name

    def __enter__(self):
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        if error_type is not None:
            return None
        return True

    def ignored(self, name: str) -> bool:
        """
        Check if the given file or folder is supposed to be ignored

        :param str name: The file or folder to check
        :return bool: To ignore or not ignore, is the question
        """
        return any(map(lambda x: x in name, self.ignored_dirs + self.ignored_files))

    def generate_import_info(self, code: str) -> dict:
        """
        Generates information related to what is imported from each module

        :param str code: Python code
        :return dict: A dict with import information for the code
        """
        r_from_import = r"from\s+([\w\.]+)\s+import\s+(.+)"
        r_mod_import = r"(?<!from.*?)(?<=import\s+)(.+)"

        from_imports = {}
        for match in regex.finditer(r_from_import, code):
            module = match.group(1)
            imports = match.group(2)
            from_imports.setdefault(module, [])
            from_imports[module].extend(regex.split(r",\s*", imports))

        return {
            "from_imports": from_imports,
            "module_imports": reduce(
                operator.iconcat, map(lambda x: regex.split(r",\s*", x), regex.findall(r_mod_import, code)), []
            )
        }

    def generate_attr_info(self, class_: str) -> dict:
        r_attr = r"self\.(\w+)(?::\s*(\w+))?\s*=\s*(.+?)\n\s{4}(?:\"\"\"(.*?)\"\"\")?"
        attrs = {}
        for match in regex.finditer(r_attr, class_):
            name = match.group(1)
            if name in attrs:
                continue
            type_ = match.group(2)
            value = match.group(3)
            docstr = match.group(4)
            attrs[name] = {
                "name": name,
                "type": type_,
                "value": value,
                "docstr": docstr.removeprefix("\n").removesuffix("\n") if match.group(4) else None
            }
        return attrs

    def generate_class_attr_info(self, class_: str, indent=4) -> dict:
        r_class_attr = rf"(?<!self\.)(?<=\n\s{{{indent}}})(\w+)(?::\s*(\w+))?\s*=\s*(.+?)\n\s{{{indent}}}(?:\"\"\"(.*?)\"\"\")?"
        class_attrs = {}
        for match in regex.finditer(r_class_attr, class_, regex.DOTALL):
            name = match.group(1)
            type_ = match.group(2)
            value = match.group(3)
            docstr = match.group(4)
            class_attrs[name] = {
                "name": name,
                "type": type_,
                "value": value,
                "docstr": remove_suffix(remove_prefix(docstr, "\n"), "\n") if match.group(4) else None
            }
        return class_attrs

    @staticmethod
    def split_params(signature: str) -> list:
        open_count = 0
        param_list = []
        param = ""
        for char in signature:
            if char == '[':
                open_count += 1
            elif char == ']':
                open_count -= 1
            if char != ',' or open_count != 0:
                param += char
            elif char == ',' and open_count == 0:
                param_list.append(param.strip())
                param = ""
        else:
            if param.strip():
                param_list.append(param.strip())
        return param_list

    def generate_function_info(self, class_: str, indent: int = 4) -> dict:
        r_functions = rf"(?:\n\s{{{indent}}}@(.+?))?\n\s{{{indent}}}def\s+(\w+)\((.*?)?\)(?:\s+->\s+(.+?))?:(?:\n\s{{{4 + indent}}}\"\"\"(.+?)\"\"\")?"
        functions = {}
        function_type = {
            "overload": "overload",
            "classmethod": "class_methods",
            "staticmethod": "static_methods",
            "property": "properties",
            "setter": "setters",
            "deleter": "deleters",
            "deprecated": "deprecated",
        }
        func_count = {}
        for match in regex.finditer(r_functions, class_, regex.DOTALL):
            decor = match.group(1)
            name = match.group(2)
            params = match.group(3)
            rtype = match.group(4)
            docstr = remove_suffix(remove_prefix(match.group(5), "\n"), "\n") if match.group(5) else None

            param_info = {}
            if params:
                r_params = r"(\*{0,2}\w+)(?::\s*(\w+))?(?:\s*=\s*(.*))?"
                for param in PyInfoGenerator.split_params(params):
                    try:
                        match = regex.match(r_params, param)
                        p_name = match.group(1)
                        type_ = match.group(2)
                        val = match.group(3)
                        param_info[p_name] = {
                            "name": p_name,
                            "type_": type_ if type_ else None,
                            "default": val,
                        }
                    except AttributeError as e:
                        print(f"{repr(param)}")
                        raise e

            func_count.setdefault(name, 0)
            func_count[name] += 1
            type_ = function_type[decor.split(".")[-1]] if decor else "method"

            if type_ == "overload":
                functions[f"{name}{func_count[name]}"] = {
                    "type": type_,
                    "name": name,
                    "docstr": docstr,
                    "return_type": rtype,
                    "params": param_info,
                }
            else:
                functions[name] = {
                    "type": type_,
                    "name": name,
                    "docstr": docstr,
                    "return_type": rtype,
                    "params": param_info,
                }

        return functions

    def _generate_class_info(self, class_: str) -> dict:

        functions = self.generate_function_info(class_)

        return {
            "class_attrs": self.generate_class_attr_info(class_),
            "attrs": self.generate_attr_info(class_),

            "methods": {key: value for key, value in filter(lambda x: x[1]["type"] == "method", functions.items())},
            "class_methods": {key: value for key, value in
                              filter(lambda x: x[1]["type"] == "class_methods", functions.items())},
            "static_methods": {key: value for key, value in
                               filter(lambda x: x[1]["type"] == "static_methods", functions.items())},
            "overloads": {key: value for key, value in filter(lambda x: x[1]["type"] == "overload", functions.items())},

            "properties": {key: value for key, value in
                           filter(lambda x: x[1]["type"] == "properties", functions.items())},
            "setters": {key: value for key, value in filter(lambda x: x[1]["type"] == "setters", functions.items())},
            "deleters": {key: value for key, value in filter(lambda x: x[1]["type"] == "deleters", functions.items())},
        }

    def generate_class_info(self, code: str) -> dict:
        """
        Generates information about each class in the file. check the dict that is returned by this function at the end
        to see all of the information that is obtained for each class

        :param str code: Python code
        :return dict: A dict with all the information about classes in the code
        """

        r_class = r"class\s+(\w+)(?:\((.*?)\))?:\n\s{4}(?:\"\"\"(.*?)\"\"\")?.*?(?=(?:\nclass\s|$))"
        classes = {}
        for match in regex.finditer(r_class, code, regex.DOTALL):
            class_code = match.group(0)
            name = match.group(1)
            parents = match.group(2)
            docstr = match.group(3)

            classes[name] = {}
            classes[name]["name"] = name
            classes[name]["docstring"] = remove_suffix(remove_prefix(docstr, "\n"), "\n") if match.group(3) else None
            if parents:
                parents = regex.split(r",\s*", parents)
                classes[name]["parents"] = list(filter(lambda x: "metaclass" not in x, parents))
                classes[name]["metaclasses"] = list(
                    map(lambda x: remove_prefix(x, "metaclass="), filter(lambda x: "metaclass" in x, parents))
                )
            else:
                classes[name]["parents"] = None
                classes[name]["metaclasses"] = None

            classes[name].update(self._generate_class_info(class_code))
        return classes

    def generate_file_info(self, file_name: str, output_file_name: str) -> None:
        """
        Outputs the json file with the information for the given python filename

        :param str file_name: The file to generate the information for
        :param str output_file_name: The file to output the json to
        """

        c_print("🔃 Generating file info for file:", colour="bright_yellow", end=" ")
        c_print(f"{file_name}", colour="bright_blue", end="")
        sys.stdout.flush()

        with open(file_name, encoding="utf-8") as file:
            code = file.read()

        code = regex.sub(r"#.*", "", code)
        code = regex.sub(r"\s*\\\s*\n\s*", "", code)

        file_info = {
            "filename": remove_prefix(file_name, self.folder_name + "\\"),
            "imports": self.generate_import_info(code),
            "classes": self.generate_class_info(code),
            "functions": self.generate_function_info(code, indent=0),
            "variables": self.generate_class_attr_info(code, indent=0)
        }

        c_print("\r✔ Generated file info for file:", colour="bright_green", end=" ")
        c_print(f"{file_name}", colour="bright_blue")

        folder = Path(output_file_name).parent
        if not folder.is_dir():
            folder.mkdir()

        with open(output_file_name, "w") as file:
            json.dump(file_info, file, indent=4)

    def generate_info(self, output_folder: str) -> None:
        """
        Outputs all the json files to the given folder

        Args:
            output_folder: The folder to output the jsons to
        """
        for root, dirs, files in os.walk(self.folder_name):
            for file in files:
                if not self.ignored(f"{root}\\{file}") and file.endswith(".py"):
                    inside_dir = remove_prefix(remove_prefix(root, self.folder_name), "\\")
                    inside_dir = inside_dir.replace("\\", ".") + "." if inside_dir else inside_dir
                    self.generate_file_info(f"{root}\\{file}", f"{output_folder}\\{inside_dir}{file}.json")


def generate_jsons(python_folder: Path, output_folder: Path):
    with PyInfoGenerator(str(python_folder.absolute())) as info_gen:
        info_gen.generate_info(str(output_folder.absolute()))


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text: str, suffix: str):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text
