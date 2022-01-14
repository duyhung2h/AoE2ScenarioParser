# 

## Functions


### .get_unit(uuid, unit_reference_id)

Get a placed unit based on it's reference id in a scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| unit_reference_id | int | - | - |

Returns: Optional['Unit']

 --- 

### .get_units(uuid, unit_reference_ids)

Get a placed unit based on it's reference id in a scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| unit_reference_ids | List | - | - |

Returns: Optional[Tuple[List['Unit'], List[int]]]

 --- 

### .get_sections(uuid)

Get the section dict of a scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[Dict[str, 'AoE2FileSection']]

 --- 

### .get_scenario_version(uuid)

Get the scenario version.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[str]

 --- 

### .get_game_version(uuid)

Get the game version.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[str]

 --- 

### .get_map_size(uuid)

Get the map size of a scenario. Scenario is selected based on the given UUID.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[int]

 --- 

### .get_terrain(uuid)

Get the map size of a scenario. Scenario is selected based on the given UUID.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[List['TerrainTile']]

 --- 

### .get_trigger(uuid, trigger_index)

Get a trigger in a scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| trigger_index | int | - | - |

Returns: Optional['Trigger']

 --- 

### .get_triggers_by_prefix(uuid, prefix)

Get the trigger version of the scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| prefix | Union | - | The prefix to check trigger names against |

Returns: Optional[List['Trigger']]

 --- 

### .get_variable_name(uuid, variable_index)

Get the variable name in a scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| variable_index | int | - | - |

Returns: Optional[str]

 --- 

### .get_trigger_version(uuid)

Get the trigger version of the scenario.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |

Returns: Optional[float]


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```