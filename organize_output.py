import os
import shutil

def organize_files():
    """
    Organizes files from a source directory into a structured destination directory
    based on parsing the filenames.
    """
    source_dir = "/home/jonathan/Desktop/NewSSD500GB/newssd/pythonProject/ComfyUI/output"
    
    destination_base_dir = source_dir

    for filename in os.listdir(source_dir):
        source_file_path = os.path.join(source_dir, filename)
        if os.path.isfile(source_file_path) and filename.endswith(".png"):
            try:
                parts = filename.split('_')
                if len(parts) < 5:
                    print(f"Skipping file with unexpected name format: {filename}")
                    continue

                shot_type = parts[0]
                character = parts[2]
                emotion = parts[3]
                
                # The angle might contain underscores, so we join the rest
                angle_parts = parts[4:-1]
                angle = "_".join(angle_parts)

                # Create the directory structure
                target_dir = os.path.join(destination_base_dir, character, shot_type, emotion, angle)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # Move the file
                source_file_path = os.path.join(source_dir, filename)
                destination_file_path = os.path.join(target_dir, filename)
                
                # To avoid errors if the script is run multiple times, check if the file is still there
                if os.path.exists(source_file_path):
                    shutil.move(source_file_path, destination_file_path)
                    print(f"Moved: {filename} -> {destination_file_path}")
                else:
                    print(f"File already moved or does not exist, skipping: {filename}")


            except IndexError as e:
                print(f"Could not parse filename: {filename}. Error: {e}")
            except Exception as e:
                print(f"An error occurred while processing {filename}. Error: {e}")

    print("\nFile organization complete.")
    print(f"All organizable files have been moved to: {destination_base_dir}")
    print(f"The original directory '{source_dir}' might now contain files that could not be parsed or are not images.")


if __name__ == "__main__":
    organize_files()
