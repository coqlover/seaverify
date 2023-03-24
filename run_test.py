# Usage:
#   python3 run_test.py -> Run all test in parallel
#   python3 run_test.py --test test_name.py -> Run a specific test

import os
import multiprocessing
import subprocess
import time
import argparse

def run_test_file(file):
    print("Running " + file)
    return subprocess.run(["python3 tests/"+file], shell=True)

def run_all_tests():
    t = time.time()
    files = [f for f in os.listdir("tests") if f.endswith(".py")]
    print(files)
    pool = multiprocessing.Pool()
    results = [pool.apply_async(run_test_file, args=(file,)) for file in files]
    pool.close()
    pool.join()
    print("----------------")
    print("All tests passed in", time.time() - t, "seconds")
    for i in range(len(results)):
        answer = results[i].get().returncode
        print("✅" if answer == 0 else "❌", files[i])
    assert(all([r.get().returncode == 0 for r in results]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run all tests.')
    parser.add_argument('--test', type=str, help='Run a specific test file')
    args = parser.parse_args()
    if args.test:
        run_test_file(args.test)
    else:
        run_all_tests()
