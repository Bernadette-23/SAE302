import time

def task(i):
    print(f"Task{i} starts")
    time.sleep(1)
    print(f"Task{i}ends")

if __name__ == '__main__':
    start=time.perf_counter()

    task(1)
    end=time.perf_counter()

    print(f"Tasks ended in {round(end-start,2)} seconds")