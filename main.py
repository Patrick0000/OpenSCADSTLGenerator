# Example: openscad -o WineRingBlind.stl   	-D "ConditionText=\"BLIND\""    	-D TextPosition=\"wine\"	ConditionRings.scad
# google python multiple subprocess
#https://stackoverflow.com/questions/30686295/how-do-i-run-multiple-subprocesses-in-parallel-and-wait-for-them-to-finish-in-py
# pyinstaller --onefile main.py
# pyinstaller --onefile "C:\Users\pdavies\Google Drive\Projects\OpenSCADSTLGen\main.py"


from tkinter import filedialog
from tkinter import *
from pathlib import Path
import os
import subprocess


# Find the orignal file
root = Tk()
initial_dir = r'C:\Users\Patrick\Google Drive\Projects\RobotMule\OpenSCAD\JointTesting'
root.filename =  filedialog.askopenfilename(initialdir = initial_dir,
        title = "Select file",filetypes = (("SCAD","*.scad"),("all files","*.*")))
filename_whole = Path(root.filename)
# filename_whole = Path(initial_dir + '\RobotMuleJointTest_V1_Planetary.scad')
file_orig_path = filename_whole.parent
file_orig_name = filename_whole.stem
file_orig_type = filename_whole.suffix
print(filename_whole)

# Search the file for the "module Assembly()" function
in_assembly_flag = 0
part_count = 0
part_list = []
full_file_name = Path().joinpath(file_orig_path, file_orig_name + file_orig_type)
# Open the original file read only as a text file
file_orig_handle = open(full_file_name, "rt")
while True:
    line = file_orig_handle.readline()

    if in_assembly_flag:
        # This is the opening brace to the assembly function
        if line == "{\n":
            print("got {")
            pass
        # Reached the end of the assembly function
        elif line == "}\n":
            print("got }")
            in_assembly_flag = 0
        # This line must be a part name function
        else:
            # Get the part name except for the whitespace and "();" characters
            line_stripped = line.strip()
            part_list.append(line_stripped[:-3])
            part_count = part_count + 1
            print("Part Count = " + str(part_count) + ", Name = " + line_stripped[:-3])

    # if this is the end of file
    if not line:
        break
    # if we found the assmebly function
    elif line == "module Assembly()\n":
        print("module Assembly()")
        in_assembly_flag = 1

# if we have a valid number of parts
openscad_cmd_list = []
p = []
if part_count > 0 and part_count < 20:
    # Make the folder where the temp .scad files will go and the .stl outputs
    try:
        file_output_path = Path().joinpath(file_orig_path, file_orig_name)
        os.mkdir(file_output_path)
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")

    for part in part_list:
        # print({"part = " + part})
        # Go back to the beginning of the file
        file_orig_handle.seek(0)
        # make a new .scad file containing just one of the parts we want
        full_file_name = Path().joinpath(file_output_path, file_orig_name + "_" + part + file_orig_type)
        file_new_handle = open(full_file_name, "w")
        wrote_part_flag = 0
        while True:
            line = file_orig_handle.readline()

            if in_assembly_flag:
                # This is the opening brace to the assembly function
                if line == "{\n":
                    file_new_handle.write(line)
                # Reached the end of the assembly function
                elif line == "}\n":
                    in_assembly_flag = 0
                # This line must be a part name function
                elif wrote_part_flag == 0:
                    file_new_handle.write(part + "();\n")
                    wrote_part_flag = 1
                # Ignore all other part functions
                else:
                    pass

            # if this is the end of file
            if not line:
                break
            # if we found the assembly function
            elif line == "module Assembly()\n":
                in_assembly_flag = 1
                file_new_handle.write(line)
            elif in_assembly_flag == 0:
                file_new_handle.write(line)

        file_new_handle.close()

        openscad_cmd = "\"C:\Program Files\OpenSCAD\openscad\" -o \"" + str(file_output_path) + "\\" + part + ".stl\" \"" + str(full_file_name) + "\""
        openscad_cmd_list.append(openscad_cmd)
        # print(openscad_cmd)
        # subprocess.call(openscad_cmd.split())
        # subprocess.call(openscad_cmd)

        # p = subprocess.Popen(openscad_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.append(subprocess.Popen(openscad_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE))

file_orig_handle.close()

# Wait for the processes to finish
print("Running...")
for i in p:
    i.wait()

print("Finished")
