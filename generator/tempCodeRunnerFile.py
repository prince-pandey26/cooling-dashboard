import csv
import random
from datetime import datetime
import time

file_path = "data/data.csv"

while True:
    temp_in = random.randint(10, 16)
    temp_out = temp_in - random.randint(1, 6)

    drop = temp_in - temp_out

    if drop >= 5:
        status = "OK"
    elif drop >= 3:
        status = "WARNING"
    else:
        status = "ERROR"

    row = [
        datetime.now(),
        temp_in,
        temp_out,
        random.randint(28, 36),
        random.randint(50, 75),
        random.randint(100, 130),
        round(random.uniform(2.0, 3.5), 2),
        status
    ]

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print("Data added:", row)
    time.sleep(5)