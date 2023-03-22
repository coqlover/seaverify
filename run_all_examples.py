import os
import time
# for all python files of the directory "examples", run them
# If it fails, fail too
t = time.time()
l = []
res = []
for file in os.listdir("examples"):
    if file.endswith(".py"):
        c = os.system("python3 examples/" + file)
        res.append(str(c) == "0")
        l.append(file)

print("--------------------")
print("All tests passed in", time.time() - t, "seconds")
for i in range(len(l)):
    print("✅" if res[i] else "❌", l[i])