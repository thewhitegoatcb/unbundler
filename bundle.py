from unbundler.reader import BundleReader
from unbundler.file_entry import FileEntry
from unbundler.bundled_file import BundeledFile, FileVariant

import struct

class InvalidBundleMagic(Exception):
    def __init__(self, expected, curent):
        super().__init__(f"Expected magic bundle: {expected}, but got: {curent}")

class UnexpectedMultipleVariants(Exception):
    pass

class Bundle:
    SUPPORTED_BUNDLES = {
        0xF0000006 : 'vt2x',
    }

    def __init__(self, name, patch, stream, external_stream) -> None:
        self.reader = None
        self.stream = stream
        self.name = name
        self.file_count = 0
        self.file_entries:List[FileEntry] = []
        self.hash = None
        self.patch = patch
        self.external_stream = external_stream
        self.extractor = None

    @staticmethod
    def parse_path(path):
        import pathlib
        import re

        re_result = re.search(r"([A-Fa-f\d]{16})(?:\.?patch_([\d]{3}))?", pathlib.Path(path).name)
        if not re_result:
            return

        patch = 000
        re_groups = re_result.groups()
        name_hash = int(re_groups[0], 16)
        if re_groups[1]:
            patch = int(re_groups[1], 10)
        
        return name_hash, patch
    
    @staticmethod
    def load(path, stream_path):
        name_hash, patch = Bundle.parse_path(path)
        stream = open(path, 'rb')
        external_stream = open(stream_path, 'rb') if stream_path else None
        return Bundle(name_hash, patch, stream, external_stream)

    def parse(self, extractor):
        self.extractor = extractor
        self._parse_header()

        if not self._parse_file_list():
            return
        
        self._parse_all_files()

    @staticmethod
    def __unpack(stream, fmt):
        size = struct.calcsize(fmt)
        buf = stream.read(size)
        return struct.unpack(fmt, buf)
    
    def _unpack(self, fmt):
        size = struct.calcsize(fmt)
        buf = self.reader.read(size)
        return struct.unpack(fmt, buf)

    def _parse_header(self):
        magic, all_decompressed_size, _padding_size = Bundle.__unpack(self.stream, '<LLL')

        if magic not in Bundle.SUPPORTED_BUNDLES:
            raise InvalidBundleMagic(Bundle.SUPPORTED_BUNDLES.keys(), magic)
        
        self.reader = BundleReader(self.stream, all_decompressed_size)
        
    def _parse_file_list(self):
        [self.file_count] = self._unpack('<L')
        self.hash = self.reader.read(256)

        for _ in range(self.file_count):
            entry = FileEntry(*self._unpack('<QQLL'))
            self.file_entries.append(entry)
        
        return self.extractor and (not self.extractor.on_entries or self.extractor.on_entries(self))
    
    def _read_next_file(self, entry: FileEntry):
        ext_hash, filename_hash, variant_count = self._unpack('<QQL')

        #if entry.type != 0 and entry.type != 2 and entry.type != 3:
        #    print(f"UNKNOWN TYPE:{entry.type}")
        
        variants = []
        total_size = 0
        for _ in range(variant_count):
            variant = FileVariant(*self._unpack('<LLL'), total_size)
            variants.append(variant)
            total_size += variant.file_size
        
        [stream_size] = self._unpack('<L')

        data = self.reader.read(total_size) # possibly seek instead
        return BundeledFile(self, ext_hash, filename_hash, variants, entry, stream_size, data)

    def _parse_all_files(self):
        if not self.extractor.on_file:
            return
        
        for entry in self.file_entries:
            file = self._read_next_file(entry)
            if not self.extractor.on_file(file):
                break

    def read_external_stream(self, offset, size):
        if self.external_stream is None:
            return b''
        self.external_stream.seek(offset)
        return self.external_stream.read(size)

