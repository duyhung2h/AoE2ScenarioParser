"""
This file is used to update the version files and generate the variable structure files.
"""
import json
from pathlib import Path

from resources.scripts.update_versions.support import mark_retrievers, dynamic_retrievers

de_folder = Path(__file__).parent.parent.parent.parent / 'AoE2ScenarioParser' / 'versions' / 'DE'
version = 'v1.44'

# x for x in de_folder.iterdir()

f = open(de_folder / version / 'structure.json', 'r')

json_content = json.load(f)

for key, section in json_content.items():
    mark_retrievers([key], section)

f.close()

# Write back to same file
f = open(de_folder / version / 'structure.json', 'w')
json.dump(json_content, f, indent=4)
f.close()

# Write variable retrievers file
f = open(de_folder / version / 'dynamic_retrievers.json', 'w')
json.dump(dynamic_retrievers, f, indent=4)
f.close()
