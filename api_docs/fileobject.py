from typing import Dict

from regex import regex

from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list
from api_docs.jinja_env import file_template


class FileObject:
    def __init__(self, output_path, content) -> None:
        self.output_path = output_path
        self.content = content

        for name, func in content['functions'].items():
            print(name, func)
            docstr = func.get('docstr', '')
            if docstr:
                _append_parameter_types_from_docstring(func)
                # exit()

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


def _append_parameter_types_from_docstring(function: Dict):
    # print(list(function.keys()))
    docstr = function.get('docstr')
    params = function.get('params')
    # print(list(params.keys()))
    variable_name = r"[a-zA-Z][a-zA-Z0-9_]*"

    if docstr is not None:
        # print(function['docstr'])
        # f"{name}: " + ' '.join([line.strip() for line in desc.splitlines()])
        for name, desc in regex.findall(
                rf"({variable_name}): ?((?:(?!(?:{variable_name}:)|(?:\n\n)).)*)", docstr, regex.DOTALL
        ):
            if name in params.keys():
                params[name]['docstr'] = desc.strip()
        # x = input()
        # if x == 'exit':
        #     exit()
