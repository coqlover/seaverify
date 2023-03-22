# Usage: python3 build.py
# Not tested

import os

# First, copy the folder "programs_verify" into "programs_py"
os.system("cp -r programs_verify programs_py")
# For every file of the folder "programs_py"
for file in os.listdir("programs_py"):
    # If the file is a python file
    if file.endswith(".py"):
        # Read the content of the file
        f = open(file)
        content = f.readlines()
        f.close()
        # Remove every line starting by @enforce or @assume or @invariant
        content = [line for line in content if not line.startswith("@enforce") and not line.startswith("@assume") and not line.startswith("@invariant")]
        # Find the first line containing "__name__ == '__main__'"
        idx = 0
        for i in range(len(content)):
            if "__name__ == '__main__'" in content[i]:
                idx = i
                break
        # Remove every line after the line containing "__name__ == '__main__'"
        content = content[:idx]
        # Transform the import of seaverify into seahorse
        content = [line.replace("seaverify", "seahorse") for line in content]
        # Write the content in a new file
        answer = open(file, "w")
        answer.write("".join(content))
        answer.close()
# Run seahorse build
os.system("seahorse build")