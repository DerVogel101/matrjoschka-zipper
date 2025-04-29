#!/usr/bin/env python3
"""
Matryoshka Zipper - A script that recursively zips files in a folder structure.

This script takes a folder path as input and creates a hierarchical zip structure:
- Each folder becomes a zip file (folder.zip)
- Inside each folder's zip, individual files are zipped (file.txt.zip)
- Subfolders are also zipped (subfolder.zip) and placed inside their parent folder's zip

Usage:
    python main.py [options] folder_path

Options:
    -d, --depth DEPTH    Maximum directory traversal depth (default: unlimited)
                         Controls how deep the script will go into subdirectories
    --keep-temp          Keep temporary zip files (default: delete temporary files)
    -v, --verbose        Enable verbose output
    -q, --quiet          Suppress all output
    -h, --help           Show this help message and exit

Output Modes:
    - Default: Shows a progress bar using tqdm
    - Verbose (-v): Shows detailed information about each operation
    - Quiet (-q): Shows no output at all

Examples:
    # Basic usage: zip all files in the 'documents' folder
    python main.py documents

    # Limit directory traversal depth to 2 levels (root folder and its immediate subfolders)
    python main.py -d 2 documents

    # Keep temporary zip files (by default they are deleted)
    python main.py --keep-temp documents

    # Enable verbose output
    python main.py -v documents

    # Suppress all output
    python main.py -q documents
"""

import argparse
import os
import uuid
import zipfile
from pathlib import Path
from tqdm import tqdm


def zip_file(file_path, output_dir=None, uuid_str=None):
    """
    Zip a single file.

    Args:
        file_path (Path): Path to the file to be zipped
        output_dir (Path, optional): Directory to save the zip file. Defaults to the same directory as the file.
        uuid_str (str, optional): UUID string to add to temporary zip files.

    Returns:
        Path: Path to the created zip file
    """
    if output_dir is None:
        output_dir = file_path.parent

    # Add UUID to temporary zip files if provided
    if uuid_str:
        zip_path = output_dir / f"{file_path.name}_{uuid_str}.zip"
    else:
        zip_path = output_dir / f"{file_path.name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        zipf.write(file_path, arcname=file_path.name)

    return zip_path


def zip_directory(dir_path, output_dir=None, uuid_str=None):
    """
    Create a zip file for a directory.

    Args:
        dir_path (Path): Path to the directory to be zipped
        output_dir (Path, optional): Directory to save the zip file. Defaults to the parent directory.
        uuid_str (str, optional): UUID string to add to temporary zip files.

    Returns:
        Path: Path to the created zip file
    """
    if output_dir is None:
        output_dir = dir_path.parent

    # Add UUID to temporary zip files if provided
    if uuid_str:
        zip_path = output_dir / f"{dir_path.name}_{uuid_str}.zip"
    else:
        zip_path = output_dir / f"{dir_path.name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        # We don't add any files here - they will be added separately
        pass

    return zip_path


def matryoshka_zip(folder_path, max_depth=None, keep_intermediate=True, verbose=False, quiet=False):
    """
    Recursively zip files and folders in a hierarchical structure.

    Args:
        folder_path (str): Path to the folder to process
        max_depth (int, optional): Maximum directory traversal depth. None means no limit.
        keep_intermediate (bool, optional): Whether to keep temporary zip files.
        verbose (bool, optional): Whether to print verbose output.
        quiet (bool, optional): Whether to suppress all output.
    """
    folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        if not quiet:
            print(f"Error: {folder_path} is not a valid directory")
        return

    # Generate a UUID for this run to identify temporary files
    run_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity

    if verbose and not quiet:
        print(f"Starting matryoshka zipping of folder: {folder_path}")
        print(f"Max depth: {max_depth if max_depth is not None else 'unlimited'}")
        print(f"Keep temporary files: {keep_intermediate}")
        print(f"Run UUID: {run_uuid}")

    # Keep track of files we've created during this run
    created_files = set()

    # Process the root folder and its contents recursively
    process_directory(folder_path, 0, max_depth, keep_intermediate, verbose, quiet, created_files, run_uuid)

    if verbose and not quiet:
        print(f"\nMatryoshka zipping complete. Created {len(created_files)} zip files.")


def process_directory(dir_path, current_depth, max_depth, keep_intermediate, verbose, quiet, created_files, uuid_str):
    """
    Process a directory, creating zip files for it and its contents.

    Args:
        dir_path (Path): Path to the directory to process
        current_depth (int): Current depth in the directory tree
        max_depth (int, optional): Maximum directory traversal depth. None means no limit.
        keep_intermediate (bool): Whether to keep temporary zip files
        verbose (bool): Whether to print verbose output
        quiet (bool): Whether to suppress all output
        created_files (set): Set to track created zip files
        uuid_str (str): UUID string to add to temporary zip files

    Returns:
        Path: Path to the zip file created for this directory
    """
    # Check if we've reached the maximum depth
    if max_depth is not None and current_depth > max_depth:
        if verbose and not quiet:
            print(f"Skipping directory {dir_path} - max depth {max_depth} reached")
        return None

    if verbose and not quiet:
        print(f"\nProcessing directory: {dir_path} (depth: {current_depth})")

    # Create a zip file for this directory
    # Don't add UUID to the final output file (root directory)
    if current_depth == 0:
        dir_zip_path = zip_directory(dir_path, uuid_str=None)
    else:
        dir_zip_path = zip_directory(dir_path, uuid_str=uuid_str)
    created_files.add(str(dir_zip_path))

    if verbose and not quiet:
        print(f"Created directory zip: {dir_zip_path}")

    # Get all files and subdirectories in this directory
    items = list(dir_path.iterdir())
    files = [item for item in items if item.is_file() and not item.name.endswith('.zip')]
    subdirs = [item for item in items if item.is_dir()]

    if verbose and not quiet:
        print(f"Files found: {len(files)}")
        print(f"Subdirectories found: {len(subdirs)}")

    # Process all files in this directory
    # Use tqdm for progress bar if not verbose and not quiet
    file_iterator = files
    if not verbose and not quiet:
        file_iterator = tqdm(files, desc=f"Processing files in {dir_path.name}", unit="file")
    elif quiet:
        file_iterator = files  # No progress bar in quiet mode

    for file_path in file_iterator:
        # Create a zip for each file
        file_zip_path = zip_file(file_path, uuid_str=uuid_str)
        created_files.add(str(file_zip_path))

        # Add the file's zip to the directory's zip
        with zipfile.ZipFile(dir_zip_path, 'a', zipfile.ZIP_DEFLATED, compresslevel=9) as dir_zipf:
            # Strip UUID from arcname for the final output
            arcname = file_zip_path.name
            if uuid_str and uuid_str in arcname:
                arcname = arcname.replace(f"_{uuid_str}", "")
            dir_zipf.write(file_zip_path, arcname=arcname)

        if verbose and not quiet:
            print(f"Zipped file: {file_path} -> {file_zip_path}")
            # Show the arcname without UUID in verbose output
            display_name = arcname if uuid_str and uuid_str in file_zip_path.name else file_zip_path.name
            print(f"Added {display_name} to {dir_zip_path.name}")

        # Remove the file's zip if not keeping temporary files
        if not keep_intermediate:
            os.remove(file_zip_path)
            if verbose and not quiet:
                print(f"Removed temporary file: {file_zip_path}")

    # Process all subdirectories
    # Use tqdm for progress bar if not verbose and not quiet
    subdir_iterator = subdirs
    if not verbose and not quiet:
        subdir_iterator = tqdm(subdirs, desc=f"Processing subdirectories in {dir_path.name}", unit="dir")
    elif quiet:
        subdir_iterator = subdirs  # No progress bar in quiet mode

    for subdir in subdir_iterator:
        # Recursively process the subdirectory
        subdir_zip_path = process_directory(
            subdir, current_depth + 1, max_depth, keep_intermediate, verbose, quiet, created_files, uuid_str
        )

        # If the subdirectory was processed (not skipped due to max_depth)
        if subdir_zip_path:
            # Add the subdirectory's zip to this directory's zip
            with zipfile.ZipFile(dir_zip_path, 'a', zipfile.ZIP_DEFLATED, compresslevel=9) as dir_zipf:
                # Strip UUID from arcname for the final output
                arcname = subdir_zip_path.name
                if uuid_str and uuid_str in arcname:
                    arcname = arcname.replace(f"_{uuid_str}", "")
                dir_zipf.write(subdir_zip_path, arcname=arcname)

            if verbose and not quiet:
                # Show the arcname without UUID in verbose output
                display_name = arcname if uuid_str and uuid_str in subdir_zip_path.name else subdir_zip_path.name
                print(f"Added {display_name} to {dir_zip_path.name}")

            # Remove the subdirectory's zip if not keeping temporary files
            if not keep_intermediate:
                os.remove(subdir_zip_path)
                if verbose and not quiet:
                    print(f"Removed temporary file: {subdir_zip_path}")

    return dir_zip_path


def main():
    """Parse command-line arguments and run the matryoshka zipper."""
    parser = argparse.ArgumentParser(
        description='Create nested zip files from a directory, like a matryoshka doll.'
    )
    parser.add_argument(
        'folder', 
        help='Path to the folder to process'
    )
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=None,
        help='Maximum directory traversal depth. Default is unlimited. Controls how deep the script will go into subdirectories.'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary zip files. Default is to delete temporary files.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output'
    )

    args = parser.parse_args()

    # Run the matryoshka zipper with the specified options
    matryoshka_zip(
        args.folder,
        max_depth=args.depth,
        keep_intermediate=args.keep_temp,
        verbose=args.verbose,
        quiet=args.quiet
    )


if __name__ == '__main__':
    main()
