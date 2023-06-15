from unbundler.bundled_file import BundeledFile
from unbundler.bundle import Bundle
from unbundler.murmur2 import murmur64str

import struct
import pathlib
import re

class LuaExtractor:
    LUA_EXT_HASH = murmur64str("lua")
    _FLAG_IS_STRIPPED = 0b00000010

    def __init__(self, output_path, flatten, ignore_path, ignore_file_hashes, decompile) -> None:
        self.extract_list = []
        self.extracted_files = set()
        self.output_path = pathlib.Path(output_path)
        self.flatten = flatten
        self.ignore_path = ignore_path
        self.ignore_file_hashes = ignore_file_hashes
        self.is_decompile = decompile

    @staticmethod
    def read_uleb128(data, offset):
        value = data[offset]
        offset += 1
        if value >= 0x80:
            bitshift = 0
            value &= 0x7f

            while True:
                byte = data[offset]
                offset += 1

                bitshift += 7
                value |= (byte & 0x7f) << bitshift

                if byte < 0x80:
                    break

        return offset, value
    
    def on_entries(self, bundle: Bundle) -> bool:
        is_lua_ext = lambda entry: (entry.ext_hash == LuaExtractor.LUA_EXT_HASH)
        self.extract_list = list(filter(is_lua_ext, bundle.file_entries))
        
        return bool(self.extract_list)
    
    def on_file(self, file: BundeledFile) -> bool:
        if file.file_entry not in self.extract_list:
            return bool(self.extract_list)
        
        if not self.ignore_file_hashes or \
        file.filename_hash not in self.ignore_file_hashes:
            self.on_lua_file(file)

        self.extract_list.remove(file.file_entry)
        return bool(self.extract_list)
    
    def decompile(self, input_path, output_path, mem):
        import ljd_lib

        print(f"Decompiling {input_path} ...")
        m = ljd_lib.Main(["-c"], is_lib=True)
        if m.process_memory(mem, input_path, output_path) == 0:
            print(f"Decompiling successful saved to: {output_path}")
        else:
            print(f"Decompiling FAILED for: {input_path}")

    def save_lua(self, path, data, bundled_file):
        if self.ignore_path:
            for ignore_re in self.ignore_path:
                if re.search(ignore_re, path):
                    return False
        
        system_path: pathlib.Path = self.output_path / path
        system_path.parent.mkdir(parents=True, exist_ok=True)

        if self.is_decompile:
            self.decompile(path, system_path, data)
            self.extracted_files.add(bundled_file.filename_hash)
            return True
        else:
            with system_path.open('wb') as file:
                print(f"Saving lua bytecode to: {system_path}")
                file.write(data)
                self.extracted_files.add(bundled_file.filename_hash)
                return True
        return False
    
    def on_lua_file(self, file: BundeledFile) -> bool:
        for variant in file.variants:
            data = file.get_variant_data(variant)
            size, unk1, unk2, magic, bc_version = struct.unpack_from("<LLL3sB", data)
            offset = 16
            offset, flags = LuaExtractor.read_uleb128(data, offset)
            if bool(flags & LuaExtractor._FLAG_IS_STRIPPED):
                print(f"No debug info for {variant.filename_hash:x}, skipping...")
            else:
                offset, length = LuaExtractor.read_uleb128(data, offset)
                path = bytes.decode(bytes(data[offset:offset+length]), 'utf-8', 'backslashreplace')
                self.save_lua(path[1:], data[12:], file)
        
        #print(f"E: {file.bundle.name:0x}.patch_00{file.bundle.patch}.{file.filename_hash:0x}.lua")
        return True
