from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario


class VariableRetrieverManager:
    def __init__(self, scenario_ref):
        self.scenario: AoE2DEScenario = scenario_ref
        self.variable_retrievers = None
        self.progress_id = -1

    def get_value(self, retriever):
        retriever_id = int(retriever['id'])

        if self.progress_id > retriever_id:
            pass  # Needs a return

        for vr_id in self.variable_retrievers.keys():
            if self.progress_id < retriever_id and self.progress_id < int(vr_id):
                vr = self.variable_retrievers[vr_id]
                print(self.get_length_until(int(vr_id)))
                print(vr)
                exit()

        print(retriever_id)
        exit()

    def get_length_until(self, rid):
        g = retriever_generator_from(self.scenario.structure, 0)
        total_length = 0
        for _ in range(rid):
            retriever = next(g)
            if str(retriever['id']) in self.variable_retrievers:
                return
            total_length += get_static_retriever_length(retriever)
        return total_length


def get_static_retriever_length(retriever):
    # Filter numbers out for length, filter text for type
    var_len = int(''.join(filter(str.isnumeric, retriever['type'])))
    var_type = ''.join(filter(str.isalpha, retriever['type']))

    if var_type == '':
        var_type = "data"

    # Divide by 8, and parse from float to int
    if var_type not in ["c", "data"]:
        var_len = int(var_len / 8)

    return var_len


def retriever_generator_from(structure, rid):
    def loop(s):
        for retriever in s['retrievers'].values():
            if retriever['type'][:7] == "struct:":
                rtype = retriever['type'][7:]
                loop(s['structs'][rtype])
            else:
                if rid <= int(retriever['id']):
                    yield retriever

    for section in structure.values():
        gen = loop(section)
        while True:
            try:
                yield next(gen)
            except StopIteration:
                break
    yield None
