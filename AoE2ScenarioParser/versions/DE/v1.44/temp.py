import json

with open('./effects.json', 'r') as file:
    json_ = json.load(file)

    for id_, content in json_.items():
        if id_ == "-1":
            continue

        keys = [key for key, value in content['default_attributes'].items() if value in [-1, "", []]]
        for key in keys:
            del content['default_attributes'][key]

    with open('./effects2.json', 'w') as file2:
        file2.write(json.dumps(json_, indent=4))
