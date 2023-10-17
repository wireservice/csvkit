import os.path
import subprocess
import timeit

num_repeats = 100  # number of repeats for timeit


def test_csvformat_performance():
    command = ['csvformat', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvformat performance test elapsed time: {elapsed} seconds")


def test_csvjson_performance():
    command = ['csvjson', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvjson performance test elapsed time: {elapsed} seconds")


def test_csvlook_performance():
    command = ['csvlook', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvlook performance test elapsed time: {elapsed} seconds")


def test_csvpy_performance():
    command = ['csvpy', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvpy performance test elapsed time: {elapsed} seconds")


def test_csvsql_performance():
    command = ['csvsql', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvsql performance test elapsed time: {elapsed} seconds")


def test_csvstat_performance():
    command = ['csvstat', os.path.join('examples', 'iris.csv')]
    start_time = timeit.default_timer()
    for _ in range(num_repeats):
        subprocess.run(command, stdout=subprocess.DEVNULL)  # redirect output to DEVNULL as we don't want to print it
    elapsed = timeit.default_timer() - start_time
    print(f"CSVKit csvstat performance test elapsed time: {elapsed} seconds")


test_csvformat_performance()
test_csvjson_performance()
test_csvlook_performance()
# test_csvpy_performance()
# test_csvsql_performance()
test_csvstat_performance()
