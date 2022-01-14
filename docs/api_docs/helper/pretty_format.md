# 

## Functions


### .pretty_format_list(plist, inline_types)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| plist | List | - | - |
| inline_types | List | - | - |

Returns: None

 --- 

### .pretty_format_dict(pdict)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| pdict | dict | - | - |

Returns: None

 --- 

### .pretty_format_name(name)

Returns a pretty-printed version of the name string.
Replaces all underscores with spaces and capitalizes the first letter
of each word.
For example, elite_chu_ko_nu -> Elite Chu Ko Nu.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| name | str | - | - |

Returns: str


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```