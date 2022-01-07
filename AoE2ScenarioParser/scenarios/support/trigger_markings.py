from typing import Union, List, Optional, Iterator, Dict
from uuid import UUID

from AoE2ScenarioParser.helper.attr_dict import AttrDict
from AoE2ScenarioParser.helper.helper import values_are_valid, value_is_valid
from AoE2ScenarioParser.objects.data_objects.condition import Condition
from AoE2ScenarioParser.objects.data_objects.effect import Effect
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger
from AoE2ScenarioParser.objects.data_objects.unit import Unit
from AoE2ScenarioParser.objects.support.area import Area
from AoE2ScenarioParser.objects.support.tile import Tile
from AoE2ScenarioParser.scenarios.scenario_store import getters, actions


class TriggerMarkings:
    _scan_options: Dict[str, List[str]] = {
        "area": ["area", "areas"],
        "tile": ["tile", "tiles"],
        "location": ["location", "locations"],
        "object": ["object", "objects"],
    }

    def __init__(self, uuid: UUID) -> None:
        super().__init__()

        self._uuid = uuid

        self.objects = AttrDict()
        self.areas = AttrDict()
        self.tiles = AttrDict()

    def discover(self, remove_template_triggers: bool) -> None:
        triggers = getters.get_triggers_by_prefix(
            self._uuid,
            tuple(val for lst in self._scan_options.values() for val in lst)
        )

        for trigger in triggers:
            object_ids = []
            tag = self._resolve_markings_name(trigger)
            for ce in loop_trigger_content(trigger):
                if trigger.name.startswith("area"):
                    area = self._create_area(ce)
                    if area:
                        self.areas.setdefault(tag, []).append(area)

                elif trigger.name.startswith(("tile", "location")):
                    tiles = self._create_tiles(ce)
                    if tiles:
                        self.tiles.setdefault(tag, []).extend(tiles)

                elif trigger.name.startswith("object"):
                    object_ids.extend(self._get_unit_ids(ce))

            if object_ids:
                self.objects.setdefault(tag, []).extend(getters.get_units(self._uuid, object_ids)[0])

        if remove_template_triggers:
            actions.remove_triggers(self._uuid, [t.trigger_id for t in triggers])

    def _create_area(self, ce: Union['Condition', 'Effect']) -> Optional[Area]:
        if values_are_valid(ce.area_x1, ce.area_y1, ce.area_x2, ce.area_y2):
            return actions.new_area_object(self._uuid).select(ce.area_x1, ce.area_y1, ce.area_x2, ce.area_y2)

    def _create_tiles(self, ce: Union['Condition', 'Effect']) -> Optional[List[Tile]]:
        tiles = []
        if isinstance(ce, Effect) and values_are_valid(ce.location_x, ce.location_y):
            tiles.append(Tile(ce.location_x, ce.location_y))
        area = self._create_area(ce)
        if area:
            tiles.extend(list(area.to_coords()))
        return tiles

    def _get_unit_ids(self, ce: Union['Condition', 'Effect']) -> List[int]:
        ids: List[int] = []
        if isinstance(ce, Condition) and values_are_valid(ce.unit_object):
            ids.append(ce.unit_object)
        elif isinstance(ce, Effect):
            if value_is_valid(ce.location_object_reference):
                ids.append(ce.location_object_reference)
            if value_is_valid(ce.selected_object_ids):
                ids.extend(ce.selected_object_ids)
        return ids

    @staticmethod
    def _resolve_markings_name(trigger: 'Trigger'):
        return trigger.name[trigger.name.find(":") + 1:]


def loop_trigger_content(trigger: 'Trigger') -> Iterator[Union['Condition', 'Effect']]:
    for condition in trigger.conditions:
        yield condition
    for effect in trigger.effects:
        yield effect
