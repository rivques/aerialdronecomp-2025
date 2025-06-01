from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction, ReadColorAndSetLEDAction, FastTakeoffAction
import logging
import utils.field_locations as fl
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, calibrate_sensors=False)

    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(), # +15 (15 total)
        FastTakeoffAction(1), # +10 (25 total)
        GoToAction(0, 0, 1, "TakeoffSettle", 3),
        # start of fig8 #1
        GoToAction(1.3, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.85, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.2, None, None, "GoToRed", 3),
        GoToAction(None, None, 1.9, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3), # +40 (65 total)
        GoToAction(0, 0, 1.2, "DescendForArch", 4),
        # start of fig8 #2
        GoToAction(1.4, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.85, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.4, None, None, "GoToRed", 3), # +40 (105 total)
        GoToAction(None, None, 1.9, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3),
        # start of arch farming
        GoToAction(0, 0, 1.2, "DescendForArch", 4),
        GoToAction(2.4, None, None, "GoThruArches", 3), # +10 (115 total)
        GoToAction(0, 0.2, None, "GoBack", 3),
        GoToAction(2.5, None, None, "GoThruArchesAgain", 3), # +10 (125 total)
        LandAction(),
        ReadColorAndSetLEDAction(), # +15 (140 total)
    ], ErrorHandlingStrategy.LAND).run_sequence()