import os
import time
# for all python files of the directory "examples", run them
# If it fails, fail too
t = time.time()
l = []
for file in os.listdir("examples"):
    if file.endswith(".py"):
        c = os.system("python3 examples/" + file)
        assert str(c) == "0"
        l.append(file)

print("All tests passed in", time.time() - t, "seconds")
print("File executed: ", l)