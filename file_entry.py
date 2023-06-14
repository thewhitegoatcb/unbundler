class FileEntry:
    def __init__(self, ext_hash, filename_hash, file_type, file_size) -> None:
        self.ext_hash = ext_hash
        self.filename_hash = filename_hash
        self.type = file_type
        self.file_size = file_size
