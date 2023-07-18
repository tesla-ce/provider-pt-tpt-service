import os


def get_config_value(key):
    secret_path = '/run/secrets'
    # Check environment variables
    value = os.getenv(key, None)
    if value is not None:
        return value
    # Check file environment variable
    file_path = os.getenv('{}_FILE'.format(key.upper()), None)
    if file_path is None:
        file_path = os.path.join(secret_path, key.upper())
    if file_path is not None and os.path.exists(file_path):
        with open(file_path, 'r') as secret:
            value = secret.read()

    return value
