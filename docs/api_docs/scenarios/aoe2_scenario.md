# 

## Functions


### .initialise_version_dependencies(game_version, scenario_version)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| game_version | - | - | - |
| scenario_version | - | - | - |

Returns: None

 --- 

### ._get_file_section_data(file_section)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| file_section | AoE2FileSection | - | - |

Returns: None

 --- 

### .get_file_version(generator)

Get first 4 bytes of a file, which contains the version of the scenario


**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| generator | IncrementalGenerator | - | - |

Returns: None

 --- 

### .decompress_bytes(file_content)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| file_content | - | - | - |

Returns: None

 --- 

### .compress_bytes(file_content)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| file_content | - | - | - |

Returns: None

 --- 

### .get_version_directory_path()



Returns: Path

 --- 

### .get_version_dependant_structure_file(game_version, scenario_version, name)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| game_version | str | - | - |
| scenario_version | str | - | - |
| name | str | - | - |

Returns: dict

 --- 

### .get_structure(game_version, scenario_version)



**Params**:

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| game_version | - | - | - |
| scenario_version | - | - | - |

Returns: dict


 
## Debug:
```json
{!{ pretty_format_dict(json) }}
```