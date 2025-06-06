from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
logging.basicConfig(level=logging.DEBUG)

AXIS_TO_TUNE = 0
if __name__ == "__main__":
    disabled_control_axes = [True, True, False, True]
    disabled_control_axes[AXIS_TO_TUNE] = False
    drone_manager = DroneManager(drone_type=DroneType.REAL, disabled_control_axes=disabled_control_axes)
    SequentialAction(drone_manager, [TakeoffAction(), GoToAction(0, 0, 0.5, timeout=3), WaitAction(4)], ErrorHandlingStrategy.LAND).run_sequence()
    while True:
        start_loc = [0, 0, 0.5]
        end_loc = [0, 0, 0.5]
        start_loc[AXIS_TO_TUNE] = 0
        end_loc[AXIS_TO_TUNE] = 1
        SequentialAction(drone_manager, [GoToAction(*start_loc, timeout=5), WaitAction(5), GoToAction(*end_loc,timeout=5), WaitAction(5)], ErrorHandlingStrategy.LAND).run_sequence()