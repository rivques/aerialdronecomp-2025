from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction, ReadColorAndSetLEDAction, FastTakeoffAction
import logging
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL)

    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(),
        FastTakeoffAction(1),
        GoToAction(0, 0, 1, "TakeoffSettle", 4),
        GoToAction(1.4, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.7, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.2, None, None, "GoToRed", 3),
        GoToAction(None, None, 1.8, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3),
        GoToAction(0, 0, 1, "TakeoffSettle", 4),
        GoToAction(1.4, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.8, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.2, None, None, "GoToRed", 3),
        GoToAction(None, None, 1.8, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3),
        LandAction()
    ], ErrorHandlingStrategy.LAND).run_sequence()