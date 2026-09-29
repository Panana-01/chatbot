import os

DATA_DIR_NAME = "Data"


def data_file(filename: str) -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, DATA_DIR_NAME, filename)
