# 

## Functions


### .rprint(string, replace, final)

Replaceable print, print lines which can be overwritten by the next




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | - | "" | - |
| replace | - | True | - |
| final | - | False | - |

Returns: None

 --- 

### .s_print(string, replace, final, color)

Status print, read rprint docstring for more info.
Simple rprint wrapper with a check for the PRINT_STATUS_UPDATES setting.



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | - | "" | - |
| replace | - | True | - |
| final | - | False | - |
| color | - | None | - |

Returns: None

 --- 

### .color_string(string, color)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| color | str | - | - |

Returns: str

 --- 

### .warn(string)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | - | "" | - |

Returns: None


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```