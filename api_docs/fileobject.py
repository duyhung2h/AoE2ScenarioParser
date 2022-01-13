from typing import Dict

from regex import regex

from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list
from api_docs.generate_json import remove_prefix, remove_suffix
from api_docs.jinja_env import file_template


class FileObject:
    def __init__(self, output_path, content) -> None:
        self.output_path = output_path
        self.content = content

        # Keys: ['type', 'name', 'docstr', 'return_type', 'params']
        for name, func in self.content['functions'].items():
            docstr: str = func.get('docstr', '')
            return_type: str = func.get('return_type', '')

            if docstr:
                _fix_param_docstr(func)
                func['docstr'] = _fix_docstring(func)

            if return_type:
                func['return_type'] = _fix_type(return_type)

            # Keys: ['name', 'type_', 'default', 'docstr']
            for param_name, param in func['params'].items():
                param_type: str = param.get('type_', '')

                if param_type:
                    param['type_'] = _fix_type(param_type)

            func['display'] = f".{name}({', '.join(func.get('params', {}).keys())})"

        super().__init__()

    def render(self) -> str:
        return file_template.render(
            json=self.content,

            **{  # Functions
                'pretty_format_dict': pretty_format_dict
            }
        )

    def write(self):
        folder = self.output_path.parent
        if not folder.is_dir():
            folder.mkdir(parents=True)

        with self.output_path.open(mode='w', encoding='utf-8') as output:
            output.write(self.render())


def _fix_docstring(function: Dict):
    docstr: str = function.get('docstr')
    look_for = ['Args:', 'Arguments:', 'Returns:', ':Author:']

    if docstr is not None:
        locations = [docstr.find(string) for string in look_for if docstr.find(string) != -1]
        if locations:
            end_of_desc = min(locations)
            docstr = docstr[:end_of_desc]

        return '\n'.join(line.strip() for line in docstr.splitlines())
    return ""


def _fix_param_docstr(function: Dict):
    docstr = function.get('docstr')
    params = function.get('params')
    variable_name = r"[a-zA-Z][a-zA-Z0-9_]*"

    if docstr is not None:
        for name, desc in regex.findall(
                rf"({variable_name}): ?((?:(?!(?:{variable_name}:)|(?:\n\n)).)*)", docstr, regex.DOTALL
        ):
            if name in params.keys():
                params[name]['docstr'] = desc.strip()


def _fix_type(type_: str):
    if 'Union[' in type_:
        start = type_.find('Union[')
        end = type_.find(']', start) + 1
        new_return_type = type_[start:end]
        new_return_type = remove_suffix(remove_prefix(new_return_type, "Union["), "]")
        new_return_type = new_return_type.replace('"', '').replace("'", "")
        new_return_type = new_return_type.replace(', ', ' | ').replace(',', ' | ')
        type_ = type_[:start] + new_return_type + type_[end:]
    return type_
