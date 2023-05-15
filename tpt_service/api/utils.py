import os


def get_config_value(key):
    return os.getenv(key, None)