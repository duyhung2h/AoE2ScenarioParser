# 

## Functions


### .vorl(retriever, value)

Variable or List




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| retriever | - | - | - |
| value | - | - | - |

Returns: None

 --- 

### .retrieve_bytes(igenerator, retriever)

Retrieves the bytes belonging to this retriever.




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| igenerator | IncrementalGenerator | - | - |
| retriever | - | - | - |

Returns: List[bytes]

 --- 

### .is_end_of_file_mark(retriever)

Returns true if the retriever is the __END_OF_FILE_MARK__ retriever else false


**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| retriever | - | - | - |

Returns: bool

 --- 

### .handle_end_of_file_mark(igenerator, retriever)

Print message when the END_OF_FILE_MARK is reached and more bytes are present.\n
You can disable this check (and thereby this message) using:\n
``>> from AoE2ScenarioParser import settings``\n
``>> settings.NOTIFY_UNKNOWN_BYTES = False``




**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| igenerator | - | - | - |
| retriever | - | - | - |

Returns: None


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```