from unbundler.bundle import Bundle
from unbundler.lua_extractor import LuaExtractor

class Main:
    def __init__(self) -> None:
        self.options = None

    def is_bundle_path(self, path):
        return path.is_file() and (path.suffix == '' or path.suffix.startswith('.patch_'))

    def get_stream_file_path(self, path):
        stream_path = path.with_suffix('.stream')
        return stream_path if stream_path.is_file() else None

    def get_patch(self, path):
        import re

        patch = 000
        re_result = re.search(r"^\.patch_([\d]{3})$", path.suffix)
        if re_result:
            re_groups = re_result.groups()
            if re_groups[0]:
                patch = int(re_groups[0], 10)
        return patch

    def get_bundles(self, path):
        import pathlib

        d = pathlib.Path(path)
        bundle_paths = []
        # iterate directory
        for entry in d.iterdir():
            # check if it a file
            if self.is_bundle_path(entry):
                bundle_paths.append(entry)
        
        return bundle_paths
    
    def get_all_bundle_patches(self, bundle_paths):
        bundle_patches = {}
        for path in bundle_paths:
            stem = path.stem

            patch = self.get_patch(path)
                
            if stem in bundle_patches:
                bundle_patches[stem][patch] = path
            else:
                bundle_patches[stem] = { patch : path }
            
        return bundle_patches
    

    def parse_all_directory(self, path, output_path, ignore_list):
        bundle_paths = self.get_bundles(path)
        bundle_patches = self.get_all_bundle_patches(bundle_paths)

        for _stem, sorted_bundle in bundle_patches.items():
            # extract first the latest patch files and add them to the list so they don't overriden with older versions
                extracted_files = set()
                for _patch, path in sorted(sorted_bundle.items(), reverse=True):
                    try:
                        extractor = LuaExtractor(output_path, False, ignore_list, extracted_files, self.options.decompile)
                        bfile = Bundle.load(path, self.get_stream_file_path(path))
                        bfile.parse(extractor)
                        extracted_files.union(extractor.extracted_files)
                    except Exception as error:
                        print(f"An exception occurred while processing {path}:", error)
                    
    def parse_bundle(self, path, output_path, ignore_list):
        extractor = LuaExtractor(output_path, False, ignore_list, None, self.options.decompile)
        bfile = Bundle.load(path, self.get_stream_file_path(path))
        bfile.parse(extractor)

    def setup_ljd(self, ljd_path):
        import sys
        import importlib.util
        
        sys.path.append(str(ljd_path.parent))
        spec = importlib.util.spec_from_file_location("ljd_lib", ljd_path) # to main.py
        ljd_lib = importlib.util.module_from_spec(spec)
        sys.modules["ljd_lib"] = ljd_lib
        spec.loader.exec_module(ljd_lib)

    def main(self):
        import args

        self.options = args.parse(None)

        if not self.options:
            print("Error parsing args, exiting!")
            return
        
        if self.options.decompile:
            self.setup_ljd(self.options.ljd_path)
        
        if self.options.file_name:
            self.parse_bundle(self.options.file_name, self.options.output, self.options.ignore_paths)
        elif self.options.folder_name:
            self.parse_all_directory(self.options.folder_name, self.options.output, self.options.ignore_paths)
        

if __name__ == "__main__":
    m = Main()
    m.main()