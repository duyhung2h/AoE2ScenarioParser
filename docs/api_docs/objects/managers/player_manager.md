# 

## Functions


### .player_list(gaia_first)

Construct a list of players where GAIA can be first, last or not in the list at all




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| gaia_first | Union | - | - |

Returns: List[PlayerId]

 --- 

### .spread_player_attributes(player_attributes, key, lst, gaia_first)

Spreads list values to player attribute dictionaries




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| player_attributes | Dict | - | - |
| key | str | - | - |
| lst | List | - | - |
| gaia_first | Union | - | - |

Returns: None


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```