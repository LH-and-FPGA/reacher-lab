import time
from pupper_hardware_interface.interface import Interface
import numpy as np

# 串口配置，按实际情况修改
PORT      = 'COM3'
BAUDRATE  = 500000
START_BYTE= 0x00

iface = Interface(port=PORT, baudrate=BAUDRATE, start_byte=START_BYTE)

iface.set_joint_space_parameters(20.0, 2.0, 2000.0)

pos1 = np.array([0.5, -1.9, -1.5, 0, 0.0, 0.0,
                 0.0, 0.0,  0.0,  0.0, 0.0, 0.0])

pos2 = np.array([0.5, -0.9, -0.0, 0.0, 0.0, 0.0,
                 0.0,  0.0,  0.0,  0.0, 0.0, 0.0])

i = 0
while True:
    iface.set_actuator_postions(pos1)
    print("pos1")
    time.sleep(2.0)
    iface.set_actuator_postions(pos2)
    print("pos2")
    time.sleep(2.0)

