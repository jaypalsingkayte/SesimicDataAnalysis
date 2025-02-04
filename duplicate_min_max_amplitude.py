import os
from copy_rename_duplicates import (
    get_user_input, create_destination_folder, count_files_with_extension,
    copy_files, write_log, create_repeated_folder
)
from duplicate_segy_amplitude_size import process_segy_files

def main():
    # Get user input for paths and file extension
    source_path, file_extension, destination_path = get_user_input()

    # Create the main destination folder
    create_destination_folder(destination_path)

    # Count the total number of files with the given extension
    total_files, repeated_files = count_files_with_extension(source_path, file_extension)
    print(str(total_files) + " files with extension " + file_extension)

    # Copy files from source to destination
    warnings, successes = copy_files(source_path, file_extension, destination_path, total_files, repeated_files)

    # Write log files for copied and warning files
    write_log(destination_path, warnings, successes)
    print("Files copied successfully!")
    print(f"Log file created at {os.path.join(destination_path, 'copy_log.txt')}!")

    if warnings:
        print(f"Warning log file created at {os.path.join(destination_path, 'warning_log.txt')}!")

    # Create the repeated files folder and process SEG-Y files within it
    repeated_folder_path = create_repeated_folder(destination_path)
    df_segy_info = process_segy_files(repeated_folder_path)

    # If needed, manipulate df_segy_info (e.g., remove columns or rename them)
    print(df_segy_info.drop(["Textual Header Hash"], axis=1))  # Example of dropping a column before displaying

if __name__ == "__main__":
    main()
