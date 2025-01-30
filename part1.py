from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction, ReadColorAndSetLEDAction, FastTakeoffAction
import logging
import utils.field_locations as fl
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL)

    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(), # +15 (15 total)
        FastTakeoffAction(1), # +10 (25 total)
        GoToAction(0, 0, 1, "TakeoffSettle", 3),
        # start of fig8 #1
        GoToAction(1.4, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.7, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.2, None, None, "GoToRed", 3),
        GoToAction(None, None, 1.9, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3), # +40 (65 total)
        GoToAction(0, 0, 1.2, "DescendForArch", 4),
        # start of fig8 #2
        GoToAction(1.4, None, None, "GoThruArch", 3),
        GoToAction(None, None, 1.8, "RaiseForOver", 3),
        GoToAction(2.4, None, None, "GoOverBlue", 3),
        GoToAction(None, None, 1.2, "LowerAroundBlue", 3),
        GoToAction(1.4, None, None, "GoToRed", 3), # +40 (105 total)
        GoToAction(None, None, 1.9, "RaiseForOver", 3),
        GoToAction(0, None, None, "GoOverRed", 3),
        # start of arch farming
        GoToAction(0, 0, 1.2, "DescendForArch", 4),
        GoToAction(2.4, None, None, "GoThruArches", 3), # +10 (115 total)
        GoToAction(0, 0.2, None, "GoBack", 3),
        GoToAction(2.4, None, None, "GoThruArchesAgain", 3), # +10 (125 total)
        LandAction()
    ], ErrorHandlingStrategy.LAND).run_sequence()

    input("Press ENTER to start Segment 2")

    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(), # +15 (140 total)
        FastTakeoffAction(fl.yellow_keyhole[2], timeout=0), # +10 (150 total)
        GoToAction(fl.mat_2[0], fl.mat_2[1], None, "ReestablishTakeoff", timeout=0), # because the drone wants to go to 0,0 on TO
        WaitAction(3),
        GoToAction(fl.yellow_keyhole[0], fl.yellow_keyhole[1]+0.2, None, "GoThruYellowKeyhole", 3), # +15 (165 total)
        GoToAction(None, fl.yellow_keyhole[1] - 0.2, None, "GoBack", 3),
        GoToAction(None, fl.green_keyhole[1], None, "GoThruYellowKeyholeAgain", 3), # +15 (180 total)
        GoToAction(None, None, fl.green_keyhole[2], "LowerForGreenKeyhole", 3),
        GoToAction(fl.green_keyhole[0]+0.2, None, None, "GoThruGreenKeyhole", 3), # +15 (195 total)
        GoToAction(fl.green_keyhole[0]-0.1, fl.green_keyhole[1], None, "GoBack", 3),
        GoToAction(fl.green_keyhole[0]+0.2, None, None, "GoThruGreenKeyholeAgain", 3), # +15 (210 total)
        GoToAction(fl.large_landing_cube[0], fl.large_landing_cube[1], None, "GoToLandingCube", 3),
        LandAction() # +25 (235 total)
    ], ErrorHandlingStrategy.LAND).run_sequence()