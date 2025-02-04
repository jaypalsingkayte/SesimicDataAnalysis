import os
import shutil
from collections import defaultdict

def clean_path(path):
    """Function to clean the path (remove double quotes if present)"""
    return path.strip('"')

def get_user_input():
    """Function to get user input for source path, file extension, and destination path"""
    source_path = clean_path(input("Enter the source folder path: "))
    file_extension = input("Enter the file extension (e.g., .txt, .jpg): ")
    destination_path = clean_path(input("Enter the destination folder path: "))
    return source_path, file_extension, destination_path

def create_destination_folder(destination_path):
    """Function to create the destination folder if it doesn't exist"""
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

def create_repeated_folder(destination_path):
    """Function to create the repeated files folder if it doesn't exist"""
    repeated_folder_path = os.path.join(destination_path, "repeated_files")
    if not os.path.exists(repeated_folder_path):
        os.makedirs(repeated_folder_path)
    return repeated_folder_path

def count_files_with_extension(source_path, file_extension):
    """Function to count the total number of files with the specific extension"""
    total_files = 0
    repeated_files = defaultdict(list)
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(file_extension):
                total_files += 1
                repeated_files[file].append(root)
    return total_files, repeated_files

def copy_files(source_path, file_extension, destination_path, total_files, repeated_files):
    """Function to copy files from source to destination and log the process"""
    warnings = []
    successes = []
    copied_files = 0
    repeated_counter = defaultdict(int)
    repeated_folder_path = create_repeated_folder(destination_path)

    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                file_name, file_ext = os.path.splitext(file)

                if len(repeated_files[file]) > 1:
                    repeated_counter[file] += 1
                    dest_file_path = os.path.join(repeated_folder_path, f"{file_name}_{repeated_counter[file]}{file_ext}")
                    repeated = True
                else:
                    dest_file_path = os.path.join(destination_path, file)
                    repeated = False

                if not os.path.exists(dest_file_path):
                    copied_files += 1
                    print(f"Copying {copied_files}/{total_files} files: {file}")
                    shutil.copy(file_path, dest_file_path)
                    successes.append((file_name + file_ext, repeated, os.path.basename(dest_file_path)))
                else:
                    warning_message = f"Couldn't copy file {file_name + file_ext} because it's the same as in {os.path.basename(dest_file_path)}"
                    print(f"**Warning**: {warning_message}")
                    warnings.append(warning_message)

    return warnings, successes

def write_log(destination_path, warnings, successes):
    """Function to write log files"""
    log_file_path = os.path.join(destination_path, "copy_log.txt")
    with open(log_file_path, 'w') as log_file:
        log_file.write("Original_File_Name,Repeated,Destination_File_Name\n")
        for success in successes:
            log_file.write(f"{success[0]},{success[1]},{success[2]}\n")

    if warnings:
        warning_log_file_path = os.path.join(destination_path, "warning_log.txt")
        with open(warning_log_file_path, 'w') as warning_log_file:
            for warning in warnings:
                warning_log_file.write(f"{warning}\n")

if __name__ == "__main__":
    source_path, file_extension, destination_path = get_user_input()
    create_destination_folder(destination_path)
    total_files, repeated_files = count_files_with_extension(source_path, file_extension)
    print(str(total_files) + " files with extension " + file_extension)

    warnings, successes = copy_files(source_path, file_extension, destination_path, total_files, repeated_files)
    write_log(destination_path, warnings, successes)

    print("Files copied successfully!")
    print(f"Log file created at {os.path.join(destination_path, 'copy_log.txt')}!")

    if warnings:
        print(f"Warning log file created at {os.path.join(destination_path, 'warning_log.txt')}")
