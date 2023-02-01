import pathlib

def count_img_in_folder(directory: str) -> int:
    num_img = 0
    for path in pathlib.Path(directory).iterdir():
        if path.is_file():
            num_img += 1
    return num_img
