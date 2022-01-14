# 

## Functions


### .add_str_trail(string)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | bytes | - | - |

Returns: bytes

 --- 

### .has_str_trail(string)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | bytes | - | - |

Returns: bool

 --- 

### .del_str_trail(string)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | Union | - | - |

Returns: str | bytes

 --- 

### .add_prefix_chars(string, char, length)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| char | str | - | - |
| length | int | - | - |

Returns: None

 --- 

### .add_suffix_chars(string, char, total_length)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| char | str | - | - |
| total_length | int | - | - |

Returns: None

 --- 

### .remove_prefix(string, prefix)

Cheap knockoff function of:
https://docs.python.org/3/library/stdtypes.html?highlight=removesuffix




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| prefix | str | - | - |

Returns: str

 --- 

### .q_str(value)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| value | any | - | - |

Returns: str

 --- 

### .trunc_string(string, length, add_ellipsis)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| length | - | 30 | - |
| add_ellipsis | - | True | - |

Returns: None

 --- 

### .trunc_bytes(string, length, add_ellipsis)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | bytes | - | - |
| length | - | 30 | - |
| add_ellipsis | - | True | - |

Returns: None

 --- 

### .add_tabs(string, tabs)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| tabs | int | - | - |

Returns: str

 --- 

### .create_inline_line(entries)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| entries | List | - | - |

Returns: None

 --- 

### .create_textual_hex(string, space_distance, enter_distance)

Please note that the 'enter_distance' parameter is including the - to be added - spaces. If you calculated it
without the spaces, please multiply the number by: `block size incl space / block size excl space`


**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| space_distance | int | 2 | - |
| enter_distance | int | 48 | - |

Returns: None

 --- 

### .insert_char(string, char, step)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| char | str | - | - |
| step | - | 64 | - |

Returns: None


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```