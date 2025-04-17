from PIL import Image
import os
import zipfile
import tempfile
import shutil

# Written using ChatGPT, used for converting comic downloaded from kox.moe
# Get the script folder
root_folder = os.path.dirname(os.path.abspath(__file__))

# Loop through all ZIP files in the folder
for item in os.listdir(root_folder):
    if item.lower().endswith('.zip'):
        zip_path = os.path.join(root_folder, item)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            modified = False

            # Walk through extracted contents
            for dirpath, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        file_path = os.path.join(dirpath, filename)
                        try:
                            with Image.open(file_path) as img:
                                if img.size == (960, 1216): #Check the resolution for specific rotated double page, it might be different
                                    rotated = img.rotate(-90, expand=True)
                                    rotated.save(file_path)
                                    modified = True
                                    print(f"Rotated: {filename} in {item}")
                        except Exception as e:
                            print(f"Error with {filename}: {e}")

            # If changes were made, rebuild the ZIP
            if modified:
                new_zip_path = zip_path  # Overwrite the original
                with zipfile.ZipFile(new_zip_path, 'w') as zip_out:
                    for foldername, _, files in os.walk(temp_dir):
                        for file in files:
                            full_path = os.path.join(foldername, file)
                            arcname = os.path.relpath(full_path, temp_dir)
                            zip_out.write(full_path, arcname)
                print(f"Updated ZIP: {item}")
