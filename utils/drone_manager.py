import functools
from codrone_edu.drone import *
import asyncio
import logging
from typing import Optional
from matplotlib.axes import Axes
import numpy as np
from simple_pid import PID
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import multiprocessing
import queue
from utils.data_logging import DataLogger

# unswizzle asyncio.sleep bc codrone swizzles it for some reason

asyncio.sleep = original_asyncio_sleep

# used for communnication of when the drone has arrived at its target
class ManagedFlightState(Enum):
    IDLE = 0
    MOVING = 2
    LANDED = 4

class DroneType(Enum):
    REAL = 0
    PROPS_OFF = 1
    FULL_SIM = 2

def yaw_clip(angle):
    # deal with wrapping yaw angle around 360˚ for PID loop
    if angle > 0:
        if angle > 180:
            return angle - 360
    else:
        if angle < -180:
            return angle + 360
    return angle

class DroneManager:
    control_frequency = 15 # Hz
    graph_update_frequency = 8 # Hz
    error_history_length = 15 # seconds
    lerp_threshold = 0.15 # m
    pid_controllers = [
        PID(70, 4, 3, setpoint=0, output_limits=(-100, 100), proportional_on_measurement=False), # x old gains: 70, 4, 3
        PID(70, 4, 3, setpoint=0, output_limits=(-100, 100), proportional_on_measurement=False), # y old gains: 70, 4, 3
        PID(150, 15, 1, setpoint=0, output_limits=(-100, 100), proportional_on_measurement=False), # z old gains: 150, 15, 1
        PID(2, 0, 0, setpoint=0, output_limits=(-100, 100), error_map=yaw_clip, proportional_on_measurement=False) # yaw old gains: 2, 0, 0
    ]

    _target_pose = np.array([0, 0, 0, 0])
    @property
    def target_pose(self):
        return self._target_pose
    @target_pose.setter
    def target_pose(self, value):
        self._target_pose = value
        for i in range(4):
            self.pid_controllers[i].setpoint = value[i] # allow for updating setpoints by just setting target pose

    _disabled_control_axes = [False, False, False, False]
    @property
    def disabled_control_axes(self):
        return self._disabled_control_axes
    @disabled_control_axes.setter
    def disabled_control_axes(self, value):
        self._disabled_control_axes = value
        for i, disabled in enumerate(self._disabled_control_axes):
            if disabled:
                self.pid_controllers[i].set_auto_mode(False, last_output=0) # allow for disabling axes via property
                self.current_output[i] = 0

    def __init__(self, event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(), drone_type = DroneType.REAL, disabled_control_axes = [False, False, False, False], parent_name = None, calibrate_sensors = True, log_filepath = "live_data.csv"):
        self.dl = DataLogger(log_filepath)
        # set up drone
        self.raw_drone: Drone = Drone()
        self.drone_type = drone_type
        if drone_type in [DroneType.REAL, DroneType.PROPS_OFF]:
            self.raw_drone.pair()
            self.raw_drone.set_drone_LED(255, 255, 255, 100)
            # calibrate sensors
            if calibrate_sensors:
                self.raw_drone.set_initial_pressure()
                self.raw_drone.reset_sensor()

        # set up drone state
        self.drone_pose: np.ndarray = np.array([0, 0, 0, 0]) # x, y, z, yaw
        self.target_pose: np.ndarray = np.array([0, 0, 0, 0])
        self.current_output: np.ndarray = np.array([0, 0, 0, 0])
        self.managed_flight_state: ManagedFlightState = ManagedFlightState.LANDED
        self.last_color = "Unknowns"
        self.ignore_next_loop_warning_flag = False
        # set up update loop
        self.event_loop = event_loop
        self.drone_update_loop = asyncio.ensure_future(self.start_update_loop(),loop=self.event_loop)

        self.disabled_control_axes = disabled_control_axes

        self.last_control_loop_time = time.monotonic()

        logging.info("DOUBLE CHECK: Controller is in LINK STATE?")

    def close(self):
        try:
            self.drone_update_loop.cancel()
        except AttributeError:
            pass
        self.raw_drone.close()
    
    async def fast_takeoff(self, altitude: float = 1.0):
        # the drone api's takeoff(), but without the sleep at the end
        self.raw_drone.reset_move()
        self.raw_drone.sendTakeOff()

        timeout = 4
        init_time = time.time()
        time_elapsed = time.time() - init_time
        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            state = self.raw_drone.get_state_data()
            state_flight = state[2]
            if state_flight is ModeFlight.TakeOff:
                break
            else:
                self.raw_drone.sendTakeOff()
                time.sleep(0.01)

        self.target_pose = np.insert(self.target_pose, 2, altitude) # keep the rest of the pose but set the altitude (idx 2)
        for controller in self.pid_controllers:
            controller.reset()


    async def takeoff(self):
        self.raw_drone.takeoff() # blocks
        self.ignore_next_loop_warning()
        self.target_pose = np.insert(self.target_pose, 2, 1) # keep the rest of the pose but set the altitude (idx 2) to 1
        for controller in self.pid_controllers:
            controller.reset()
    
    async def land(self):
        self.raw_drone.land() # blocks
        self.ignore_next_loop_warning()
        self.target_pose = np.insert(self.target_pose, 2, 0) # keep the rest of the pose but set the altitude (idx 2) to 0
        self.managed_flight_state = ManagedFlightState.LANDED
    
    async def start_update_loop(self):
        while True:
            await self.poll_drone()
    
    async def poll_drone(self):
        df = self.dl.get_df()
        df["step_start_time"] = time.monotonic()
        # drone state docs at https://docs.robolink.com/docs/codrone-edu/python/Sensors/24-get_sensor_data
        if self.drone_type in [DroneType.FULL_SIM]:
            self.drone_pose = self.target_pose
        else:
            drone_state = self.raw_drone.get_sensor_data()
            self.drone_pose = np.array([drone_state[16], drone_state[17], drone_state[18], drone_state[14]])
        df["x_current"] = self.drone_pose[0]
        df["y_current"] = self.drone_pose[1]
        df["z_current"] = self.drone_pose[2]
        df["yaw_current"] = self.drone_pose[3]
        df["x_target"] = self.target_pose[0]
        df["y_target"] = self.target_pose[1]
        df["z_target"] = self.target_pose[2]
        df["yaw_target"] = self.target_pose[3]
        df["x_error"] = self.target_pose[0] - self.drone_pose[0]
        df["y_error"] = self.target_pose[1] - self.drone_pose[1]
        df["z_error"] = self.target_pose[2] - self.drone_pose[2]
        df["yaw_error"] = yaw_clip(self.target_pose[3] - self.drone_pose[3])

        # calculate gains
        for i, disabled in enumerate(self.disabled_control_axes):
            if disabled:
                self.current_output[i] = 0
            else:
                self.current_output[i] = self.pid_controllers[i](self.drone_pose[i])
        
        df["x_output"] = self.current_output[0]/100
        df["y_output"] = self.current_output[1]/100
        df["z_output"] = self.current_output[2]/100
        df["yaw_output"] = self.current_output[3]/100

        if self.drone_type in [DroneType.REAL]:
            # set gains
            self.raw_drone.set_pitch(self.current_output[0])
            self.raw_drone.set_roll(-self.current_output[1]) # roll is negative for some reason
            self.raw_drone.set_throttle(self.current_output[2])
            self.raw_drone.set_yaw(self.current_output[3])
            self.raw_drone.move()

        poll_end_time = time.monotonic()
        seconds_per_loop = poll_end_time - self.last_control_loop_time
        self.last_control_loop_time = poll_end_time


        logging.debug(f"Drone polled, pose now {np.array2string(self.drone_pose, precision=3)} (target {np.array2string(self.target_pose)}, error {np.linalg.norm(self.drone_pose[:3] - self.target_pose[:3])})")
        logging.debug(f"Drone gains: x {self.current_output[0]}, y {self.current_output[1]}, z {self.current_output[2]}, yaw {self.current_output[3]}")
        logging.debug(f"Control loop took {seconds_per_loop*1000:.3f} ms ({1/seconds_per_loop:.1f} Hz)")
        if 1/seconds_per_loop < self.control_frequency/1.5:
            if self.ignore_next_loop_warning_flag:
                self.ignore_next_loop_warning_flag = False
            else:
                logging.warn(f"Control loop took {seconds_per_loop*1000:.3f} ms ({1/seconds_per_loop:.1f} Hz) (target {self.control_frequency} Hz, alarm at {self.control_frequency/1.5:.1f} Hz). Is something loading the CPU? ")
        self.dl.log(df)
        await asyncio.sleep(max(0, 1/self.control_frequency - seconds_per_loop))        

    async def go_to_abs(self, x: Optional[float], y: Optional[float], z: Optional[float], yaw: Optional[float] = None, timeout: Optional[float] = None):
        # None means don't change that value
        target_x = x if x is not None else self.target_pose[0]
        target_y = y if y is not None else self.target_pose[1]
        target_z = z if z is not None else self.target_pose[2]
        target_yaw = yaw if yaw is not None else self.target_pose[3]
        
        self.target_pose = np.array([target_x, target_y, target_z, target_yaw])

        if timeout is not None:
            start_time = time.monotonic()

        self.managed_flight_state = ManagedFlightState.MOVING
        while True:
            await asyncio.sleep(1/self.control_frequency)
            # check if we're close enough to the target
            if np.linalg.norm(self.drone_pose[:3] - np.array([target_x, target_y, target_z])) < self.lerp_threshold:
                break
            if timeout is not None and time.monotonic() - start_time > timeout:

                logging.warning(f"GoToAction timed out {np.linalg.norm(self.drone_pose[:3] - np.array([target_x, target_y, target_z])):.3f} meters off-target")
                break
        self.managed_flight_state = ManagedFlightState.IDLE
    
    async def go_to_rel(self, x: float, y: float, z: float):
        target_x = self.drone_pose[0] + x
        target_y = self.drone_pose[1] + y
        target_z = self.drone_pose[2] + z

        await self.go_to_abs(target_x, target_y, target_z)

    def get_colors(self, set_led=True):
        if self.drone_type not in [DroneType.FULL_SIM]:
            color_raw = [0, 0]
            counter = 0
            while color_raw[1] == 0 and counter < 16:
                color_raw = self.raw_drone.get_color_data()
                counter += 1
                logging.debug(f"Color sensor read {color_raw} (counter {counter})")
                time.sleep(0.25)
            if counter >= 16:
                logging.error("Color sensor failed to read")
                if set_led:
                    self.raw_drone.set_drone_LED(255, 0, 0, 100)
                return "Red"
            color = "Unknown"

            if color_raw[1] > 300 or color_raw[1] < 60:
                color = "Red"
                if set_led:
                    for _ in range(5):
                        self.raw_drone.set_drone_LED(255, 0, 0, 100)
                        time.sleep(0.1)
            elif color_raw[1] > 60 and color_raw[1] < 180:
                color = "Green"
                if set_led:
                    for _ in range(5):
                        self.raw_drone.set_drone_LED(0, 255, 0, 100)
                        time.sleep(0.1)
            elif color_raw[1] > 180 and color_raw[1] < 300:
                color = "Blue"
                if set_led:
                    for _ in range(5):
                        self.raw_drone.set_drone_LED(0, 0, 255, 100)
                        time.sleep(0.1)
            self.last_color = color
            return color
        else:
            return "Red"
    def ignore_next_loop_warning(self):
        # call this if you've blocked for a while and already know you've messed up the control loop timing
        self.ignore_next_loop_warning_flag = True