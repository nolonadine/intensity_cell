import os
import glob

from deformationcytometer.includes.includes import getInputFolder

# get the inputfolder to process
parent_folder = getInputFolder()

# get all the avi files in the folder and its subfolders
files = glob.glob(f"{parent_folder}/**/*.avi", recursive=True) + glob.glob(f"{parent_folder}/**/*.tif", recursive=True)
files_fluorescence = [x for x in files if not "B" in x]

print(f"selected {parent_folder} with {len(files_fluorescence)} files")

i = 0
# iterate over the files
for file in files_fluorescence:
    if file.endswith("_raw.avi") or file.endswith("_raw.tif"):
        continue
    # and call extract_frames_shapes.py on each file
    os.system(f'python intensity.py "{file}"')
    #os.system(f'python deformationcytometer/detection/detect_nucleus.py "{file2}"')
