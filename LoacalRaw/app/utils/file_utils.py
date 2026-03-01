import os

SUPPORTED_IMAGE_EXTENSIONS = (
    ".jpg", ".jpeg",
    ".png",
    ".cr2", ".nef", ".arw", ".dng"
)

def is_supported_image(file_path):
    return file_path.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)

def get_files_in_folder(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if os.path.isfile(full_path) and is_supported_image(full_path):
            files.append(full_path)
    return files
