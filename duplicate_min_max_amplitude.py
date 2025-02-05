import os
from copy_rename_duplicates import (
    get_user_input, create_destination_folder, count_files_with_extension,
    copy_files, write_log, create_repeated_folder
)

def process_segy_files(folder_path):
    """Function to process SEG-Y files and extract relevant details"""
    print(f"📂 Processing SEG-Y files in: {folder_path}")

    # Dummy return value (replace with actual processing logic)
    # If using pandas, return a DataFrame instead of None
    return None  # Or return a pandas DataFrame

def main():
    try:
        # Get user input for paths and file extension
        source_path, file_extension, destination_path = get_user_input()

        # Create the main destination folder
        create_destination_folder(destination_path)

        # Count the total number of files with the given extension
        total_files, repeated_files = count_files_with_extension(source_path, file_extension)
        print(f"🔍 {total_files} files found with extension {file_extension}")

        # Copy files from source to destination
        warnings, successes = copy_files(source_path, file_extension, destination_path, total_files, repeated_files)

        # Write log files for copied and warning files
        write_log(destination_path, warnings, successes)
        print("✅ Files copied successfully!")
        print(f"📄 Log file created at: {os.path.join(destination_path, 'copy_log.txt')}!")

        if warnings:
            print(f"⚠️ Warning log file created at: {os.path.join(destination_path, 'warning_log.txt')}!")

        # Create the repeated files folder
        repeated_folder_path = create_repeated_folder(destination_path)

        # Import process_segy_files inside function to avoid circular import
        from duplicate_min_max_amplitude import process_segy_files  # ✅ Fix circular import

        # Process SEG-Y files in the repeated files folder
        df_segy_info = process_segy_files(repeated_folder_path)

        # If needed, manipulate df_segy_info (e.g., remove columns or rename them)
        if df_segy_info is not None:
            print(df_segy_info.drop(columns=["Textual Header Hash"], errors="ignore"))  # Safe column drop

    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
