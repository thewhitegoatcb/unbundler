def parse(args):
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(
                    description='Unpacks stingray bundle files')
    
    parser.add_argument('-f', metavar='--file', type=pathlib.Path, dest="file_name", nargs='?', help='input bundle file')
    parser.add_argument('-d', metavar='--directory', type=pathlib.Path, dest="folder_name", nargs='?', help='input bundle folder')
    parser.add_argument('-o', metavar='--output', type=pathlib.Path, dest="output", required=True, help='output file path when -f/--file is used or folder path for -d/--directory')
    parser.add_argument('-s', metavar='--skip-patches', type=bool, dest="skip_patchs", help='skip patch files')
    parser.add_argument('-i', metavar='--ignore', type=str, dest="ignore_paths", nargs='*', help='regular expression to ignore file paths')
    parser.add_argument('-D', '--decompile', dest="decompile", action='store_true', help='decompile lua files and place them in the output folder')
    parser.add_argument('-j', metavar='--ljd', type=pathlib.Path, dest="ljd_path", default='./ljd/main.py', help='ljd path, needs a special version of LJD to work')

    opt = parser.parse_args(args)

    if opt.file_name and opt.folder_name:
        print("Can't use both -f/--file and -d/--directory at the same time!")
        return None
    
    if opt.file_name:
        if not opt.file_name.is_file():
            print(f"{opt.file_name} doesn't exist or not a file!")
            return None
    elif opt.folder_name:
        if not opt.folder_name.is_dir():
            print(f"{opt.folder_name} doesn't exist or not a folder!")
            return None
    else:
        print("Must have at least one input -f/--file or -d/--directory!")
        return None
    
    if opt.decompile:
        ljd_path = opt.ljd_path
        if ljd_path.is_dir():
            ljd_path = ljd_path / 'main.py'
        if not ljd_path.is_file():
            print(f"Couldn't locate LJD at {ljd_path}")
            return None
        
    return opt