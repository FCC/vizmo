import configparser
import os


class Config():
    """
    Singleton object representing the parsed configuration for the project. By default the configuration object is
    stored one directly up from the source code and is named 'vizmocfg.ini'
    """

    _config = None
    _config_dict = None

    def __new__(cls, *args, **kwargs):
        if not cls._config:
            prev_dir = os.getcwd()
            os.chdir('..')
            cls._config = configparser.ConfigParser()
            cls._config.read('vizmocfg.ini')
            cls._config_dict = _to_dict(cls._config)
            os.chdir(prev_dir)

        return cls._config_dict


def _to_dict(parser):
    """
    For the given config parser, create a dictionary with each config entry mapped to it.

    Args:
        parser - ConfigParser object to read the config from.
    Returns:
        A dictionary with the config entries.
    """

    config_dict = {}
    lists = []
    for section in parser.sections():
        if section in ('lists',):
            for entry in parser[section]:
                lists.append(entry)

    for section in parser.sections():
        if section in lists:
            l = [entry for entry in parser[section] if bool(parser[section][entry])]
            config_dict.update({section: l})
        else:
            sub_dict = {}
            for entry in parser[section]:
                l = parser[section][entry]
                sub_dict.update({entry: l})
            config_dict.update({section: sub_dict})

    return config_dict

