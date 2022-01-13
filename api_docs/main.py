import json
from pathlib import Path
from typing import Dict, List

from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list
from api_docs.fileobject import FileObject

mkdocs_yml_start = "# << INJECT API DOC LINES AFTER >>"
mkdocs_yml_end = "# << INJECT API DOC LINES BEFORE >>"

source = Path(__file__).parent.parent / 'AoE2ScenarioParser'
target = Path(__file__).parent / 'generated'

file_index = 0
file_count = 5


def generate_from_templates():
    global file_index
    paths: Dict = {}
    insert_strings: List[str] = []

    path_list = Path(target).glob('**/*.py.json')
    for path in path_list:
        loop_ref = paths
        new_file_name = path.name.replace('.py.json', '').replace('.', '/') + ".md"

        output_path = Path(__file__).parent.parent / "docs" / "api_docs" / new_file_name
        with path.open(mode="r") as file:
            file = json.load(file)

        file_obj = FileObject(
            output_path=output_path,
            content=file
        )
        file_obj.write()

        for part in new_file_name[:-3].split('/'):
            loop_ref.setdefault(part, {})
            loop_ref = loop_ref[part]

    def rec(dct: Dict, pre):
        pre_folders = "" if len(pre) == 0 else '/'.join(pre) + "/"

        for key, sub in dct.items():
            file_path, yml_key = "", key
            if len(sub) == 0:  # If there's no content in 'folder' (aka it's a file)
                file_path = f'"api_docs/{pre_folders}{key}.md"'
                yml_key = f'{key.split("/")[-1]}'

            insert_strings.append(f"{(2 + len(pre)) * '  '}- {yml_key}: {file_path}")

            if len(sub):
                rec(dct[key], pre + [key])

    rec(paths, [])
    print(pretty_format_list(insert_strings))

    with (Path(__file__).parent.parent / 'mkdocs.yml').open(mode="r+") as f:
        content = f.read()
        f.seek(0)

        start = content.find(mkdocs_yml_start)
        end = content.find(mkdocs_yml_end)

        if start != -1 and end != -1:
            start += len(mkdocs_yml_start)
            insertion = '\n'.join(insert_strings)
            f.write(f"{content[:start]}\n{insertion}\n{' ' * 4}{content[end:]}")


if __name__ == '__main__':
    # generate_jsons(source, target)
    generate_from_templates()
