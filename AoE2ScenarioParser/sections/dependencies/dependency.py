import math
from typing import TYPE_CHECKING

from AoE2ScenarioParser.sections.dependencies.dependency_action import DependencyAction

if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.retrievers.retriever import Retriever


def refresh_targets(retriever_event, section, sections):
    for target in retriever_event.dependency_target.targets:
        selected_retriever = select_retriever(target, section, sections)
        # selected_retriever = get_retriever_by_name(retriever_list, target[1])
        # selected_retriever = section.retriever_map[target[1]]
        execute_refresh_action(selected_retriever, section, sections)


def execute_refresh_action(retriever, section, sections):
    handle_retriever_dependency(retriever, "refresh", section, sections)


def handle_retriever_dependency(retriever: 'Retriever', state, section, sections):
    if not hasattr(retriever, f'on_{state}'):
        return

    retriever_event = getattr(retriever, f'on_{state}')  # on_construct, on_commit or on_refresh

    action = retriever_event.dependency_action

    if action == DependencyAction.REFRESH_SELF:
        execute_refresh_action(retriever, section, sections)
    elif action == DependencyAction.REFRESH:
        refresh_targets(retriever_event, section, sections)
    elif action in [DependencyAction.SET_VALUE, DependencyAction.SET_REPEAT]:
        value = execute_dependency_eval(retriever_event, section, sections)
        if action == DependencyAction.SET_VALUE:
            retriever.data = value
        elif action == DependencyAction.SET_REPEAT:
            retriever.datatype.repeat = value


def execute_dependency_eval(retriever_event, section, sections):
    eval_code = retriever_event.dependency_eval.eval_code
    eval_locals = retriever_event.dependency_eval.eval_locals
    targets = retriever_event.dependency_target.targets

    values = []
    for target in targets:
        # retriever_list = select_retriever_list(target, self_list, sections)
        # values.append(get_retriever_by_name(retriever_list, target[1]).data)
        values.append(select_retriever(target, section, sections).data)

    for index, target in enumerate(targets):
        eval_locals[target[1]] = values[index]
    eval_locals['math'] = math

    return eval(eval_code, {}, eval_locals)


def select_retriever(target, section, sections):
    if target[0] == "self":
        return section[target[1]]
    else:
        return sections[target[0]][target[1]]
