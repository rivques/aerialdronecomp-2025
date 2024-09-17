# how quickly can we write to a file (including flushing) in python?
# result: 10-100kHz, more than enough
# see https://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-file for the other side
import time
with open("filespeedtest.csv", "w") as f:
    f.write("A,B,C,D,E,F,G,H,I,J")
    f.flush()
    start_time = time.time()
    for i in range(100_000):
        f.write(f"\n{time.time()},{10*i},{10*i+1},{10*i+2},{10*i+3},{10*i+4},{10*i+5},{10*i+6},{10*i+7},{10*i+8}")
        f.flush()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
    print(f"time per write: {(end_time - start_time) / 10_000}")
    print(f"writes per second: {10_000 / (end_time - start_time)}")