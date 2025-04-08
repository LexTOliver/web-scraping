import yaml


def load_config(file_path: str) -> dict:
    """
    Load the configuration file.

    Parameters:
        file_path - str: The path to the configuration file

    Returns:
        dict: The configuration data
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config
