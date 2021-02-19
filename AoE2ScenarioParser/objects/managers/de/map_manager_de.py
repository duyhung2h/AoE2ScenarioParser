from typing import List

from AoE2ScenarioParser.helper.retriever_object_link import RetrieverObjectLink
from AoE2ScenarioParser.objects.data_objects.terrain_tile import TerrainTile
from AoE2ScenarioParser.objects.managers.map_manager import MapManager


class MapManagerDE(MapManager):

    _link_list = [
        RetrieverObjectLink("map_color_mood", "Map", "map_color_mood"),
        RetrieverObjectLink("collide_and_correct", "Map", "collide_and_correct"),
        RetrieverObjectLink("villager_force_drop", "Map", "villager_force_drop"),
        RetrieverObjectLink("map_width", "Map", "map_width"),
        RetrieverObjectLink("map_height", "Map", "map_height"),
        RetrieverObjectLink("terrain", "Map", "terrain_data", process_as_object=TerrainTile),
        RetrieverObjectLink("script_name", "Map", "script_name"),
    ]

    def __init__(self,
                 map_color_mood: str,
                 collide_and_correct: bool,
                 villager_force_drop: bool,
                 map_width: int,
                 map_height: int,
                 terrain: List[TerrainTile],
                 script_name: str
                 ):

        self.map_color_mood = map_color_mood
        self.collide_and_correct = collide_and_correct
        self.villager_force_drop = villager_force_drop
        self.script_name = script_name

        super().__init__(map_width, map_height, terrain)
