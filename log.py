import logging
import os
import datetime

import database
import config


def config_decorator(func):
    """
    Decorator for injecting the project config. The config is automatically read in and parsed into a dictionary.
    """

    config_dict = config.Config()
    db = database.Connection('private')
    Logger()

    def inner(*args, **kwargs):
        kwargs.update({'_config': config_dict})
        kwargs.update({'db': db})
        kwargs.update({'log': Logger})
        return func(*args, **kwargs)
    return inner


class Logger():
    """
    Singleton logger object.

    On init this class will build a new log if new_log is set to True. The naming scheme is prefex-date-[i].log where i
    is an index that starts at 1 and continues counting until a name with that index is available for that date.
    """

    _initialized = False

    def __new__(cls, *args, new_log=False, **kwargs):
        if not cls._initialized:
            cls._initialized = True

            # Read in the log path and file name from the config file.
            parser = config.Config()
            log_file_name = parser['util']['log_file_name']
            log_path = parser['util']['log_path']

            # Build the final log file name by appending the date onto the prefix a number if necessary.
            today = "{:%Y%m%d}".format(datetime.datetime.today())

            index = 1
            file_name = log_file_name + '-' + today + '.log'
            file_names = os.listdir(log_path)

            if new_log:
                while True:
                    try:
                        open(log_path + file_name, 'r')
                        file_name = log_file_name + '-' + today + '-' + str(index) + '.log'
                        index += 1
                        continue
                    except FileNotFoundError:
                        break

                logging.basicConfig(filename=log_path + file_name, level=logging.INFO)
            else:
                temp_file_name = file_name
                while temp_file_name in file_names:
                    file_name = temp_file_name
                    temp_file_name = log_file_name + '-' + today + '-' + str(index) + '.log'
                    index += 1
                logging.basicConfig(filename=log_path + file_name, level=logging.INFO)


    @staticmethod
    def info(message):
        logging.info(" ** " + str(datetime.datetime.now()) + " ** " + message)

    @staticmethod
    def warning(message):
        logging.warning(" ** " + str(datetime.datetime.now()) + " ** " + message)

    @staticmethod
    def error(message):
        logging.error(" ** " + str(datetime.datetime.now()) + " ** " + message)


def init_new_log():
    Logger(new_log=True)