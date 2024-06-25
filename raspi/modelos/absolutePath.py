import os

def get_absolute_path():
    """
    Get the absolute path of the current file.

    Returns:
        str: The absolute path of the current file.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir
