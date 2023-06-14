# Stingray Bundle Unpacker

The Stingray Bundle Unpacker is a Python script that allows you to unpack Stingray bundle files. It provides a command-line interface with several options to control the unpacking process.

Currently it only unpacks Lua bytecode files with optional decompilation. If you want a more capable unpacker check the awesome [Bundle Unpacker](https://gitlab.com/lschwiderski/vt2_bundle_unpacker)

## Installation


   ```shell
   git clone https://github.com/thewhitegoatcb/unbundler.git
   cd unbundler
   git submodule update --init --recursive
   ```

## Usage

Run the script with the desired options to unpack Stingray bundle files.

```shell
python main.py {-f|-d file_or_folder} {-o output_folder} [-D] [-j path/to/ljd/main.py]
```

## Options

The following options are available:

- `-f, --file <file_name>`: Specifies the input bundle file to unpack.
- `-d, --directory <folder_name>`: Specifies the input bundle folder to unpack.
- `-o, --output <output>`: Specifies the output file path when `-f/--file` is used or the folder path for `-d/--directory`. This option is required.
- `-i, --ignore <ignore_paths>`: Specifies regular expressions to ignore file paths. Multiple patterns can be provided.
- `-D, --decompile`: Enables decompilation of Lua files and places them in the output folder.
- `-j, --ljd <ljd_path>`: Specifies the path to the LJD tool. By default, it assumes the path is `./ljd/main.py`.

**Note:** You cannot use both `-f/--file` and `-d/--directory` options at the same time. You must provide at least one input file or folder.

## Examples

1. Unpack a bundle file:

   ```shell
   python main.py -f my_bundle.bundle -o output_folder
   ```

2. Unpack a bundle folder, decompile Lua files, and specify a custom LJD path:

   ```shell
   python main.py -d bundle/ -o output_folder -D -j path/to/ljd/main.py
   ```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.