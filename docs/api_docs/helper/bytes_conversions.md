# 

## Functions


### .bytes_to_fixed_chars(byte_elements)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_elements | bytes | - | - |

Returns: str

 --- 

### .fixed_chars_to_bytes(string, var_len)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | - |
| var_len | int | - | - |

Returns: bytes

 --- 

### .bytes_to_str(byte_elements, charset, fallback_charset)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_elements | - | - | - |
| charset | - | settings.MAIN_CHARSET | - |
| fallback_charset | - | settings.FALLBACK_CHARSET)-> Union[str, bytes]: | - |

Returns: None

 --- 

### .str_to_bytes(string, charset, fallback_charset)

Converts string to bytes based on given charsets




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| string | str | - | The string to convert |
| charset | - | settings.MAIN_CHARSET | The main charset used while encoding |
| fallback_charset | - | settings.FALLBACK_CHARSET | The fallback charset when the main fails |

Returns: None

 --- 

### .bytes_to_int(byte_elements, endian, signed)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_elements | - | - | - |
| endian | - | "little" | - |
| signed | - | False | - |

Returns: None

 --- 

### .int_to_bytes(integer, length, endian, signed)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| integer | int | - | - |
| length | - | - | - |
| endian | - | "little" | - |
| signed | - | True | - |

Returns: None

 --- 

### .bytes_to_float(byte_elements)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_elements | - | - | - |

Returns: None

 --- 

### .float_to_bytes(f)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| f | - | - | - |

Returns: None

 --- 

### .bytes_to_double(byte_elements)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_elements | - | - | - |

Returns: None

 --- 

### .double_to_bytes(d)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| d | - | - | - |

Returns: None

 --- 

### .parse_val_to_bytes(retriever, val)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| retriever | - | - | - |
| val | - | - | - |

Returns: None

 --- 

### .parse_bytes_to_val(retriever, byte_elements)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| retriever | - | - | - |
| byte_elements | - | - | - |

Returns: None

 --- 

### ._combine_int_str(byte_string, length, endian, signed, retriever)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| byte_string | - | - | - |
| length | - | - | - |
| endian | - | - | - |
| signed | - | - | - |
| retriever | - | - | - |

Returns: bytes


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```