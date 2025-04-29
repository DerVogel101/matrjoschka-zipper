# Matryoshka Zipper

A Python utility that recursively zips files in a folder structure, creating a hierarchical zip structure similar to Russian nesting dolls (Matryoshka).

## Description

Matryoshka Zipper takes a folder path as input and creates a hierarchical zip structure:
- Each folder becomes a zip file (folder.zip)
- Inside each folder's zip, individual files are zipped (file.txt.zip)
- Subfolders are also zipped (subfolder.zip) and placed inside their parent folder's zip

This creates a nested structure where each file and directory is individually zipped, making it useful for:
- Creating archives with multiple layers of compression
- Organizing files in a hierarchical structure
- Testing zip extraction tools
- Educational purposes to demonstrate recursive file operations

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package installer) or uv (Python package installer)

### Install from source
```bash
# Clone the repository
git clone https://github.com/yourusername/matrjoschka-zipper.git
cd matrjoschka-zipper

# Install the package using pip
pip install .

# Or install the package using uv
uv pip install .
```

## Usage

```bash
python main.py [options] folder_path
```

### Options

- `-d, --depth DEPTH` - Maximum directory traversal depth (default: unlimited)
                       Controls how deep the script will go into subdirectories
- `--keep-temp` - Keep temporary zip files (default: delete temporary files)
- `-v, --verbose` - Enable verbose output
- `-q, --quiet` - Suppress all output
- `-h, --help` - Show help message and exit

### Output Modes

- **Default**: Shows a progress bar using tqdm
- **Verbose** (`-v`): Shows detailed information about each operation
- **Quiet** (`-q`): Shows no output at all

### Examples

Basic usage - zip all files in the 'documents' folder:
```bash
python main.py documents
```

Limit directory traversal depth to 2 levels (root folder and its immediate subfolders):
```bash
python main.py -d 2 documents
```

Keep temporary zip files (by default they are deleted):
```bash
python main.py --keep-temp documents
```

Enable verbose output:
```bash
python main.py -v documents
```

Suppress all output:
```bash
python main.py -q documents
```

## How It Works

1. The script generates a unique UUID for the current run to identify temporary files
2. It processes the root directory and creates a zip file for it
3. For each file in the directory:
   - It creates a zip file for the file
   - It adds the file's zip to the directory's zip
   - It removes the file's zip if not keeping temporary files
4. For each subdirectory:
   - It recursively processes the subdirectory
   - It adds the subdirectory's zip to the parent directory's zip
   - It removes the subdirectory's zip if not keeping temporary files
5. The final result is a single zip file for the root directory, containing zipped files and subdirectories

## Dependencies

- tqdm - For displaying progress bars

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
