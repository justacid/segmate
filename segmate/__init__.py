def get_version():
    version_info = (0, 10, 1)
    return ".".join(str(c) for c in version_info)

__version__ = get_version()
