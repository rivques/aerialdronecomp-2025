from codrone_edu.drone import *

drone = Drone()
drone.pair()
print("timestamp,baro_alt,dist_alt,pos_alt,dist_again_alt")

while True:
    # get all the different height indications
    sensor_data = drone.get_sensor_data()
    timestamp = sensor_data[0]
    sensor_baro = sensor_data[3]
    sensor_dist = sensor_data[4]
    sensor_pos = sensor_data[18]
    sensor_dist_again = sensor_data[21]
    print(f"{timestamp},{sensor_baro},{sensor_dist},{sensor_pos},{sensor_dist_again}")