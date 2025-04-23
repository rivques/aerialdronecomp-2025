from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction, ReadColorAndSetLEDAction, FastTakeoffAction
import logging
import utils.field_locations as fl
logging.basicConfig(level=logging.INFO)

X_DRIFT_COEFF = 1
Y_DRIFT_COEFF = 1

if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL)

    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(), # +15 (140 total)
        TakeoffAction(), # +10 (150 total)
        GoToAction(None, None, fl.yellow_keyhole[2]-0.1, "TakeoffSettle", 3),
        WaitAction(3),
        GoToAction(fl.yellow_keyhole[0]+0.1*X_DRIFT_COEFF, fl.yellow_keyhole[1]-0.2, None, "GoThruYellowKeyhole", 3), # +15 (165 total)
        # GoToAction(fl.yellow_keyhole[0]+0.1*X_DRIFT_COEFF, fl.yellow_keyhole[1] + 0.2 + 0.6*Y_DRIFT_COEFF, None, "GoBack", 3),
        # GoToAction(0.1, fl.green_keyhole[1]+0.4, None, "GoThruYellowKeyholeAgain", 3), # +15 (180 total)
        GoToAction(None, None, fl.green_keyhole[2]+0.05, "LowerForGreenKeyhole", 4),
        GoToAction(fl.green_keyhole[0]-0.2, None, None, "GoThruGreenKeyhole", 3), # +15 (195 total)
        GoToAction(fl.green_keyhole[0]+0.2 + 0.6*X_DRIFT_COEFF, None, None, "GoBack", 3),
        GoToAction(fl.green_keyhole[0]-0.2, None, None, "GoThruGreenKeyholeAgain", 3), # +15 (210 total)
        GoToAction(fl.large_landing_cube[0]+0.35*X_DRIFT_COEFF, fl.large_landing_cube[1]+0.9*Y_DRIFT_COEFF, None, "GoToLandingCube", 3),
        LandAction() # +25 (235 total)
    ], ErrorHandlingStrategy.LAND).run_sequence()