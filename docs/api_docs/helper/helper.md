# 

## Functions


### .xy_to_i(x, y, map_size)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| x | - | - | - |
| y | - | - | - |
| map_size | - | - | - |

Returns: int

 --- 

### .i_to_xy(i, map_size)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| i | - | - | - |
| map_size | - | - | - |

Returns: Tile

 --- 

### .value_is_valid(value)

Check if value is valid by making sure it's not -1 nor None




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| value | Any | - | - |

Returns: bool

 --- 

### .values_are_valid(*args)

Check if value is valid by making sure it's not -1 nor None




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| *args | Any | - | - |

Returns: bool

 --- 

### .get_enum_from_unit_const(const)

Returns an Enum corresponding with the given Const.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| const | int | - | The constant representing a unit |

Returns: InfoDatasetBase | None

 --- 

### .get_int_len(num)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| num | - | - | - |

Returns: None

 --- 

### .exclusive_if(*args)

Returns True if exactly one entry is true. False otherwise


**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| *args | - | - | - |

Returns: bool

 --- 

### .raise_if_not_int_subclass(values)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| values | - | - | - |

Returns: None

 --- 

### .validate_coords(x1, y1, x2, y2)

Validates given coordinates.

- Swaps x/y1 with x/y2 if 1 is higher than it's 2 counterpart
- Sets x/y2 to x/y1 if it's not been set.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| x1 | int | - | The X location of the left corner |
| y1 | int | - | The Y location of the left corner |
| x2 | int | None | The X location of the right corner |
| y2 | int | None | The Y location of the right corner |

Returns: Tuple[int, int, int, int]


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```