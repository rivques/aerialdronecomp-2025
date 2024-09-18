from utils import data_logging
import time
import random

dl = data_logging.DataLogger("live_data.csv")
base_number = 0
while True:
    base_number += 16
    df = dl.get_df()
    df["step_start_time"] = time.time()
    df["x_target"] = base_number+1
    df["x_current"] = base_number+2
    df["x_output"] = base_number+3
    df["x_error"] = base_number+4
    df["y_target"] = base_number+5
    df["y_current"] = base_number+6
    df["y_output"] = base_number+7
    df["y_error"] = base_number+8
    df["z_target"] = base_number+9
    df["z_current"] = base_number+10
    df["z_output"] = base_number+11
    df["z_error"] = base_number+12
    df["yaw_target"] = base_number+13
    df["yaw_current"] = base_number+14
    df["yaw_output"] = base_number+15
    df["yaw_error"] = base_number+16
    dl.log(df)
    time.sleep(0.05)
    if random.random() < 0.03:
        base_number = 0
        print("Resetting base number")