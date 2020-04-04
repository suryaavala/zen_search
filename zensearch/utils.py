from zensearch.config import RELATIONSHIPS, ENTITY_TITLE_FIELDS
from zensearch.entity_engine import Entity
import os


def get_entity_relationships(entity_name):
    return RELATIONSHIPS[entity_name]


def get_entity_title(entity_name):
    return ENTITY_TITLE_FIELDS[entity_name]


def _auto_find_file_names(entity_names, datadir):
    files_found = []
    files_in_dir = os.listdir(os.path.abspath(datadir))
    for name in entity_names:
        matches = [os.path.basename(f) for f in files_in_dir if name in f]
        if len(matches) > 1:
            raise LookupError(
                f"Multiple files with keyword {name} found in dir {datadir}. Try specifying file names explicitly"
            )
        elif len(matches) < 1:
            raise LookupError(f"File with keyword {name} not found in dir {datadir}")
        else:
            files_found.extend(matches)
    return files_found


def get_setup_entities(entity_names, data_files):

    if isinstance(data_files, str):
        if os.path.isdir(data_files):
            files = _auto_find_file_names(entity_names, data_files)
            data_dir = data_files
            data_files = [os.path.join(data_dir, file_name) for file_name in files]
        else:
            raise TypeError(
                "Invalid data_files given. data_files should be a directory path to files or list() of file paths themselves"
            )
    elif not isinstance(data_files, list):
        raise TypeError(
            "Invalid data_files given. data_files should be a directory path to files or list() of file paths themselves"
        )

    if len(entity_names) != len(data_files):
        raise ValueError("Entity names and data files should be of same length")

    entities = {}
    for name, data_file in zip(entity_names, data_files):
        ent = Entity(name)
        ent.load_data_build_indices(os.path.abspath(data_file))
        entities[name] = ent

    return entities


def strtobool(value):
    if value in ["True", "true"]:
        return True
    elif value in ["False", "false"]:
        return False
    else:
        return value


def get_user_input(prompt):
    return strtobool(str(input(prompt)))


def get_related_match_string(core_pharse, match_number):
    if match_number != 0:
        return f"{core_pharse}_{match_number+1}"
    else:
        return core_pharse
