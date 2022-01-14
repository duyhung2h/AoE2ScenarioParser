# 

## Functions


### .unit_change_ownership1(uuid, player, unit)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| player | Union | - | - |
| unit | - | - | - |

Returns: None

 --- 

### .unit_change_ownership2(uuid, player, units)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | - |
| player | Union | - | - |
| units | List | - | - |

Returns: None

 --- 

### .unit_change_ownership(uuid, player, *args)

Change the unit(s) ownership.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | The UUID of the scenario |
| player | Union | - | The player to transfer the units to. |
| *args | - | - | - |

Returns: None

 --- 

### .import_triggers(uuid, triggers, insert_index)

Import triggers into the scenario using the trigger manager.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | The UUID of the scenario |
| triggers | List | - | The trigger to import. |
| insert_index | int | -1 | The insert index used in import triggers function |

Returns: None

 --- 

### .remove_triggers(uuid, trigger_ids)

Import triggers into the scenario using the trigger manager.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | The UUID of the scenario |
| trigger_ids | List | - | A list of trigger ids to remove. |

Returns: None

 --- 

### .new_area_object(uuid)

Creates a new area object.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| uuid | UUID | - | The UUID of the scenario |

Returns: Optional['Area']


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```