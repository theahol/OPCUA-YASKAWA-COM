#From Lars Tingelstad moto - sim -... 

from moto.sim.motosim import ControlGroupSim, MotoSim
from moto.sim.motion_controller_simulator import (
    MotionControllerSimulator,
    JointTrajectoryPoint,
)

import numpy as np
import time
import socket

m = MotoSim("localhost", [ControlGroupSim(0, 6, np.deg2rad([270.0, 0.0, 190.0, 0.0, 200.0, 0.0]))])
m.start()


while True:
    pass

