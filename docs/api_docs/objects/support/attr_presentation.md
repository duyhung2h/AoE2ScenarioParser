# 

## Functions


### ._format_trigger_id_representation(id_, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| id_ | int | - | - |
| uuid | UUID | - | - |

Returns: str

 --- 

### ._format_variable_id_representation(id_, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| id_ | int | - | - |
| uuid | UUID | - | - |

Returns: str

 --- 

### ._format_unit_reference_representation(ref_id, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| ref_id | Union | - | - |
| uuid | UUID | - | - |

Returns: str

 --- 

### .transform_effect_attr_value(effect_type, attr, val, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| effect_type | - | - | - |
| attr | - | - | - |
| val | - | - | - |
| uuid | - | - | - |

Returns: None

 --- 

### .transform_condition_attr_value(condition_type, attr, val, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| condition_type | - | - | - |
| attr | - | - | - |
| val | - | - | - |
| uuid | - | - | - |

Returns: None

 --- 

### .transform_attr_value(ce, type_, attr, val, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| ce | - | - | - |
| type_ | - | - | - |
| attr | - | - | - |
| val | - | - | - |
| uuid | - | - | - |

Returns: None

 --- 

### .get_presentation_value(key, source, type_)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| key | - | - | - |
| source | - | - | - |
| type_ | - | - | - |

Returns: None

 --- 

### .transform_value_by_representation(representation, value, uuid)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| representation | - | - | - |
| value | - | - | - |
| uuid | - | - | - |

Returns: None


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```