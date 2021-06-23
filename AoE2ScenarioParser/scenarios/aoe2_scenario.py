import json
import zlib
from pathlib import Path
from typing import Union, List, TYPE_CHECKING

import AoE2ScenarioParser.datasets.conditions as conditions
import AoE2ScenarioParser.datasets.effects as effects
from AoE2ScenarioParser.helper.exceptions import InvalidScenarioStructureError, UnknownScenarioStructureError, \
    UnknownStructureError
from AoE2ScenarioParser.helper.incremental_generator import IncrementalGenerator
from AoE2ScenarioParser.helper.printers import s_print
from AoE2ScenarioParser.helper.string_manipulations import create_textual_hex, split_string_at_index
from AoE2ScenarioParser.objects.aoe2_object_manager import AoE2ObjectManager
from AoE2ScenarioParser.objects.managers.map_manager import MapManager
from AoE2ScenarioParser.objects.managers.trigger_manager import TriggerManager
from AoE2ScenarioParser.objects.managers.unit_manager import UnitManager
from AoE2ScenarioParser.sections.aoe2_file_section import AoE2FileSection
from AoE2ScenarioParser.sections.dynamic_retriever_manager import DynamicRetrieverManager as Drm, resolve_path
from AoE2ScenarioParser.sections.sectiondict import SectionDict


if TYPE_CHECKING:
    from AoE2ScenarioParser.sections.retrievers.retriever import Retriever


class AoE2Scenario:
    @property
    def trigger_manager(self) -> TriggerManager:
        return self._object_manager.managers['Trigger']

    @property
    def unit_manager(self) -> UnitManager:
        return self._object_manager.managers['Unit']

    @property
    def map_manager(self) -> MapManager:
        return self._object_manager.managers['Map']

    def __init__(self):
        self.read_mode = None
        self.scenario_version = "???"
        self.game_version = "???"

        # File contents
        self.compressed_file = None
        self.decompressed_file = None
        # Structure
        self.structure: dict = {}
        self.sections: dict = {}
        # Managers
        self._drm: Drm = Drm()
        self._object_manager: Union[AoE2ObjectManager, None] = None

        # Injection
        self._drm.scenario = self

    def get_retriever(self, path: List or str) -> Union['Retriever', 'SectionDict']:
        if type(path) is str:
            path = path.split(".")
        sections = self.sections
        for p in path:
            sections = sections[p]
        return sections

    # Todo: Can be removed once drm function has been split
    @property
    def file_content(self):
        """Request the file content thus far."""
        return self.decompressed_file if self.decompressed_file is not None else self.compressed_file

    @classmethod
    def from_file(cls, filename, game_version):
        scenario = cls()

        print(f"\nReading file: '{filename}'")
        s_print("Reading scenario file...")
        igenerator = IncrementalGenerator.from_file(filename)
        scenario.compressed_file = igenerator.file_content
        s_print("Reading scenario file finished successfully.", final=True)

        scenario.read_mode = "from_file"
        scenario.game_version = game_version
        scenario.scenario_version = get_file_version(igenerator)

        # Log game and scenario version
        print("\n############### Attributes ###############")
        print(f">>> Game version: '{scenario.game_version}'")
        print(f">>> Scenario version: {scenario.scenario_version}")
        print("##########################################")

        s_print(f"\nLoading scenario structure...")
        scenario._load_structure()
        scenario._load_dynamic_retrievers()
        scenario._initialise_sections()

        load_trigger_version_dependencies(scenario.game_version, scenario.scenario_version)
        s_print(f"Loading scenario structure finished successfully.", final=True)

        scenario._load_file(igenerator)

        # scenario._initialize(igenerator)
        # s_print("Parsing scenario file...", final=True)
        # scenario._load_header_section(igenerator)
        # scenario._load_content_sections(igenerator)
        # s_print(f"Parsing scenario file finished successfully.", final=True)

        scenario._object_manager = AoE2ObjectManager(
            sections=scenario.sections,
            game_version=scenario.game_version,
            scenario_version=scenario.scenario_version
        )
        # scenario._object_manager.setup()

        return scenario

    def _load_structure(self):
        if self.game_version == "???" or self.scenario_version == "???":
            raise ValueError("Both game and scenario version need to be set to load structure")
        self.structure.update(get_structure(self.game_version, self.scenario_version))

    def _load_file(self, raw_file_igenerator: IncrementalGenerator):
        # Calculate all dynamic retrievers until this point
        end_of_header_id = resolve_path(self.structure, ['FileHeader', '__END_OF_HEADER_MARK__'])['id']

        # Todo: necessary because `get_length_until` doesn't reolve retrievers
        self._drm.determine_value(['FileHeader', '__END_OF_HEADER_MARK__'])
        header_length = self._drm.get_length_until(end_of_header_id)

        header, body = split_string_at_index(raw_file_igenerator.file_content, header_length)
        body = decompress_bytes(body)

        self.decompressed_file = header + body

    def _load_dynamic_retrievers(self):
        self._drm.dynamic_retrievers = get_version_dependant_structure_file(
            self.game_version, self.scenario_version, 'dynamic_retrievers'
        )

    def _initialise_sections(self):
        for section_name in self.structure.keys():
            self.sections[section_name] = SectionDict(drm=self._drm, parent_path=[section_name])

    def _load_content_sections(self, raw_file_igenerator: IncrementalGenerator):
        data_igenerator = IncrementalGenerator(
            name='Scenario Data',
            file_content=decompress_bytes(raw_file_igenerator.get_remaining_bytes())
        )

        for section_name in self.structure.keys():
            if section_name == "FileHeader":
                continue
            try:
                section = self._create_and_load_section(section_name, data_igenerator)
                self._add_to_sections(section)
            except (ValueError, TypeError) as e:
                print(f"\n[{e.__class__.__name__}] AoE2Scenario.parse_file: \n\tSection: {section_name}\n")
                self.write_error_file(trail_generator=data_igenerator)
                raise e

    def _create_and_load_section(self, name, igenerator):
        s_print(f"\t🔄 Parsing {name}...")
        section = AoE2FileSection.from_structure(
            name, self.structure.get(name),
            SectionDict(drm=self._drm)
        )
        s_print(f"\t🔄 Gathering {name} data...")
        section.set_data_from_generator(igenerator, self.sections)
        s_print(f"\t✔ {name}", final=True)
        return section

    def _add_to_sections(self, section):
        self.sections[section.name] = section

    """ ##########################################################################################
    ####################################### Write functions ######################################
    ########################################################################################## """

    def write_to_file(self, filename, skip_reconstruction=False):
        """
        Write the scenario to a new file

        Args:
            filename (str): The location to write the file to
            skip_reconstruction (bool): If reconstruction should be skipped. If true, this will ignore all changes made
                using the managers (For example all changes made using trigger_manager).
        """
        self._write_from_structure(filename, skip_reconstruction)

    def _write_from_structure(self, filename, skip_reconstruction=False):
        if not skip_reconstruction:
            self._object_manager.reconstruct()

        s_print("\nFile writing from structure started...", final=True)
        binary = self._get_file_section_data(self.sections.get('FileHeader'))

        binary_list_to_be_compressed = []
        for file_part in self.sections.values():
            if file_part.name == "FileHeader":
                continue
            binary_list_to_be_compressed.append(self._get_file_section_data(file_part))
        compressed = compress_bytes(b''.join(binary_list_to_be_compressed))

        with open(filename, 'wb') as f:
            f.write(binary + compressed)

        s_print("File writing finished successfully.", final=True)
        print(f"File successfully written to: '{filename}'")

    def _get_file_section_data(self, file_section: AoE2FileSection):
        s_print(f"\t🔄 Reconstructing {file_section.name}...")
        value = file_section.get_data_as_bytes()
        s_print(f"\t✔ {file_section.name}", final=True)
        return value

    def write_error_file(self, filename="error_file.txt", trail_generator=None):
        self._debug_byte_structure_to_file(filename=filename, trail_generator=trail_generator)

    """ #############################################
    ################ Debug functions ################
    ############################################# """

    # def _debug_write_from_source(self, filename, datatype, write_bytes=True):
    #     """This function is used as a test debugging writing. It writes parts of the read file to the filesystem."""
    #     print("File writing from source started with attributes " + datatype + "...")
    #     file = open(filename, "wb" if write_bytes else "w")
    #     selected_parts = []
    #     for t in datatype:
    #         if t == "f":
    #             selected_parts.append(self._file)
    #         elif t == "h":
    #             selected_parts.append(self._file_header)
    #         elif t == "d":
    #             selected_parts.append(self._decompressed_file_data)
    #     parts = None
    #     for part in selected_parts:
    #         if parts is None:
    #             parts = part
    #             continue
    #         parts += part
    #     file.write(parts if write_bytes else create_textual_hex(parts.hex()))
    #     file.close()
    #     print("File writing finished successfully.")

    def _retrieve_byte_structure(self, file_part):
        s_print(f"\t🔄 Writing {file_part.name}...")
        value = file_part.get_byte_structure_as_string(self.sections)
        s_print(f"\t✔ {file_part.name}", final=True)
        return value

    def _debug_byte_structure_to_file(self, filename, trail_generator: IncrementalGenerator = None, commit=False):
        """ Used for debugging - Writes structure from read file to the filesystem in a easily readable manner. """
        if commit and hasattr(self, '_object_manager'):
            self._object_manager.reconstruct()

        s_print("\nWriting structure to file...", final=True)
        with open(filename, 'w', encoding="utf-8") as f:
            result = []
            for section in self.sections.values():
                result.append(self._retrieve_byte_structure(section))

            if trail_generator is not None:
                s_print("\tWriting trail...")
                trail = trail_generator.get_remaining_bytes()

                result.append(f"\n\n{'#' * 27} TRAIL ({len(trail)})\n\n")
                result.append(create_textual_hex(trail.hex(), space_distance=2, enter_distance=24))
                s_print("\tWriting trail finished successfully.", final=True)

            f.write(''.join(result))
        s_print("Writing structure to file finished successfully.", final=True)


def load_trigger_version_dependencies(game_version, scenario_version):
    condition_json = get_version_dependant_structure_file(game_version, scenario_version, "conditions")

    for condition_id, structure in condition_json.items():
        condition_id = int(condition_id)

        conditions.condition_names[condition_id] = structure['name']
        conditions.default_attributes[condition_id] = structure['default_attributes']
        conditions.attributes[condition_id] = structure['attributes']

    effect_json = get_version_dependant_structure_file(game_version, scenario_version, "effects")

    for effect_id, structure in effect_json.items():
        effect_id = int(effect_id)

        effects.effect_names[effect_id] = structure['name']
        effects.default_attributes[effect_id] = structure['default_attributes']
        effects.attributes[effect_id] = structure['attributes']


def get_file_version(generator: IncrementalGenerator):
    """Get first 4 bytes of a file, which contains the version of the scenario"""
    return generator.get_bytes(4, update_progress=False).decode('ASCII')


def decompress_bytes(file_content: bytes) -> bytes:
    return zlib.decompress(file_content, -zlib.MAX_WBITS)


def compress_bytes(file_content):
    # https://stackoverflow.com/questions/3122145/zlib-error-error-3-while-decompressing-incorrect-header-check/22310760#22310760
    deflate_obj = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = deflate_obj.compress(file_content) + deflate_obj.flush()
    return compressed


def get_version_directory_path() -> Path:
    return Path(__file__).parent.parent / 'versions'


def get_version_dependant_structure_file(game_version: str, scenario_version: str, name: str) -> dict:
    try:
        vdir = get_version_directory_path()
        with (vdir / game_version / f'v{scenario_version}' / f'{name}.json').open() as structure_file:
            return json.load(structure_file)
    except FileNotFoundError:  # Unsupported version
        v = f"{game_version}:{scenario_version}"
        raise UnknownStructureError(f"The structure {name}.json could not be found with: {v}")


def get_structure(game_version, scenario_version) -> dict:
    try:
        vdir = get_version_directory_path()
        with (vdir / game_version / f'v{scenario_version}' / 'structure.json').open() as structure_file:
            structure = json.load(structure_file)

            if "FileHeader" not in structure.keys():
                raise InvalidScenarioStructureError(f"First section in structure should always be FileHeader.")
            return structure
    except FileNotFoundError:  # Unsupported version
        v = f"{game_version}:{scenario_version}"
        raise UnknownScenarioStructureError(f"The version {v} is not supported by AoE2ScenarioParser. :(") from None
